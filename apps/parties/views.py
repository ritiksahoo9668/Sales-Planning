from django.contrib import messages
from django.db import transaction
from django.db.models import Exists, OuterRef, Prefetch, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView, DetailView, ListView, UpdateView, View

from apps.common.mixins import AuditMixin, ERPLoginRequiredMixin
from apps.masters.choices import PartyRoleType, PartyStatusFilter
from apps.parties.forms import (
    BankDetailFormSet,
    CommercialProfileForm,
    ContactPersonFormSet,
    PartyDocumentFormSet,
    PartyForm,
    StatutoryDetailForm,
)
from apps.parties.models import (
    BankDetail,
    CommercialProfile,
    ContactPerson,
    Party,
    PartyDocument,
    PartyRole,
    StatutoryDetail,
)
from apps.masters.models import VendorSubCategory
from apps.transporters.forms import TransporterProfileForm, TruckFormSet
from apps.transporters.models import TransporterProfile
from apps.vendors.forms import VendorProfileForm
from apps.vendors.models import VendorProfile


class PartyListView(ERPLoginRequiredMixin, ListView):
    model = Party
    template_name = 'parties/party_list.html'
    context_object_name = 'parties'
    paginate_by = 10
    allowed_page_sizes = (5, 10, 20, 50)

    def get_paginate_by(self, queryset):
        try:
            per_page = int(self.request.GET.get('per_page', self.paginate_by))
        except (TypeError, ValueError):
            return self.paginate_by
        if per_page in self.allowed_page_sizes:
            return per_page
        return self.paginate_by

    def get_queryset(self):
        qs = Party.objects.filter(is_deleted=False)
        search = self.request.GET.get('q', '').strip()
        role = self.request.GET.get('role', '').strip()
        if role and role not in PartyRoleType.values:
            role = ''

        status = self.request.GET.get('status', '').strip()
        if status == PartyStatusFilter.ACTIVE:
            qs = qs.filter(is_active=True)
        elif status == PartyStatusFilter.INACTIVE:
            qs = qs.filter(is_active=False)

        if search:
            qs = qs.filter(
                Q(name__icontains=search)
                | Q(code__icontains=search)
                | Q(mobile_no__icontains=search)
                | Q(email__icontains=search)
            )

        if role:
            # Exists avoids duplicate rows / PostgreSQL DISTINCT+ORDER BY issues
            qs = qs.filter(
                Exists(
                    PartyRole.objects.filter(
                        party_id=OuterRef('pk'),
                        role=role,
                        is_active=True,
                        is_deleted=False,
                    )
                )
            )

        return qs.prefetch_related(
            Prefetch(
                'roles',
                queryset=PartyRole.objects.filter(is_active=True, is_deleted=False),
            )
        ).order_by('-created_at')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['search_query'] = self.request.GET.get('q', '').strip()
        role_filter = self.request.GET.get('role', '').strip()
        if role_filter not in PartyRoleType.values:
            role_filter = ''
        ctx['role_filter'] = role_filter
        ctx['role_filter_label'] = dict(PartyRoleType.choices).get(role_filter, '')
        ctx['role_choices'] = PartyRoleType.choices
        status_filter = self.request.GET.get('status', '').strip()
        if status_filter not in PartyStatusFilter.values:
            status_filter = ''
        ctx['status_filter'] = status_filter
        ctx['status_filter_label'] = dict(PartyStatusFilter.choices).get(status_filter, '')
        ctx['status_choices'] = PartyStatusFilter.choices
        ctx['is_filtered'] = bool(ctx['search_query'] or role_filter or status_filter)
        page_obj = ctx.get('page_obj')
        ctx['filtered_count'] = (
            page_obj.paginator.count if page_obj is not None else len(ctx.get('parties', []))
        )
        per_page = self.get_paginate_by(None)
        ctx['per_page'] = per_page
        ctx['per_page_choices'] = self.allowed_page_sizes
        if page_obj is not None:
            ctx['page_range'] = page_obj.paginator.get_elided_page_range(
                page_obj.number,
                on_each_side=2,
                on_ends=1,
            )
        params = self.request.GET.copy()
        params.pop('page', None)
        ctx['query_string'] = params.urlencode()
        return ctx

    def render_to_response(self, context, **response_kwargs):
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return render(
                self.request,
                'parties/_party_list_results.html',
                context,
                **response_kwargs,
            )
        return super().render_to_response(context, **response_kwargs)


class PartyCreateView(ERPLoginRequiredMixin, AuditMixin, CreateView):
    model = Party
    form_class = PartyForm
    template_name = 'parties/party_form.html'
    success_url = reverse_lazy('parties:party_list')

    @transaction.atomic
    def form_valid(self, form):
        self.object = form.save()
        messages.success(
            self.request,
            f'Business partner {self.object.code} — {self.object.name} created successfully.',
        )
        return redirect(self.get_success_url())

    def form_invalid(self, form):
        messages.error(self.request, 'Could not save partner. Please fix the errors below.')
        return super().form_invalid(form)


class PartyUpdateView(ERPLoginRequiredMixin, AuditMixin, UpdateView):
    model = Party
    form_class = PartyForm
    template_name = 'parties/party_form.html'

    def get_queryset(self):
        return Party.objects.filter(is_deleted=False).prefetch_related('roles')

    def get_success_url(self):
        return reverse('parties:party_detail', kwargs={'pk': self.object.pk})

    def form_valid(self, form):
        messages.success(self.request, 'Business partner updated successfully.')
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, 'Could not update partner. Please fix the errors below.')
        return super().form_invalid(form)


class PartyDetailView(ERPLoginRequiredMixin, DetailView):
    model = Party
    template_name = 'parties/party_detail.html'
    context_object_name = 'party'

    def get_queryset(self):
        return Party.objects.filter(is_deleted=False).prefetch_related(
            Prefetch(
                'roles',
                queryset=PartyRole.objects.filter(is_active=True).select_related(
                    'vendor_profile',
                    'transporter_profile',
                    'commercial_profile',
                ),
            )
        )


class PartyRoleManageView(ERPLoginRequiredMixin, View):
    """Tabbed ERP form for managing all details of a party role."""

    template_name = 'parties/party_role_manage.html'

    def get_party_role(self):
        return get_object_or_404(
            PartyRole.objects.select_related('party').prefetch_related(
                'bank_details', 'contacts', 'documents'
            ),
            pk=self.kwargs['role_pk'],
            party_id=self.kwargs['pk'],
            is_deleted=False,
        )

    def get_context(self, party_role, forms=None):
        ctx = {
            'party': party_role.party,
            'party_role': party_role,
            'role_label': party_role.get_role_display(),
        }
        if forms:
            ctx.update(forms)
        else:
            ctx.update(self.build_forms(party_role))
        if party_role.role == PartyRoleType.VENDOR:
            ctx['vendor_subcategories'] = list(
                VendorSubCategory.objects.filter(
                    is_active=True, is_deleted=False,
                ).values('id', 'name', 'category_id')
            )
        return ctx

    def build_forms(self, party_role, post_data=None, files=None):
        commercial, _ = CommercialProfile.objects.get_or_create(party_role=party_role)
        statutory, _ = StatutoryDetail.objects.get_or_create(party_role=party_role)

        kwargs = {'instance': commercial}
        statutory_kwargs = {'instance': statutory}
        if post_data is not None:
            kwargs['data'] = post_data
            statutory_kwargs['data'] = post_data
            statutory_kwargs['files'] = files

        forms = {
            'commercial_form': CommercialProfileForm(**kwargs),
            'statutory_form': StatutoryDetailForm(**statutory_kwargs),
            'bank_formset': BankDetailFormSet(
                post_data, files, instance=party_role, prefix='bank'
            ) if post_data is not None else BankDetailFormSet(instance=party_role, prefix='bank'),
            'contact_formset': ContactPersonFormSet(
                post_data, instance=party_role, prefix='contact'
            ) if post_data is not None else ContactPersonFormSet(instance=party_role, prefix='contact'),
            'document_formset': PartyDocumentFormSet(
                post_data, files, instance=party_role, prefix='document'
            ) if post_data is not None else PartyDocumentFormSet(instance=party_role, prefix='document'),
        }

        if party_role.role == PartyRoleType.VENDOR:
            vendor, _ = VendorProfile.objects.get_or_create(
                party_role=party_role,
                defaults={'company_name': party_role.party.name},
            )
            vkwargs = {'instance': vendor}
            if post_data is not None:
                vkwargs['data'] = post_data
            forms['vendor_form'] = VendorProfileForm(**vkwargs)

        if party_role.role == PartyRoleType.TRANSPORTER:
            transporter, _ = TransporterProfile.objects.get_or_create(party_role=party_role)
            transporter = TransporterProfile.objects.prefetch_related(
                'trucks__drivers'
            ).get(pk=transporter.pk)
            tkwargs = {'instance': transporter}
            if post_data is not None:
                tkwargs['data'] = post_data
            forms['transporter_form'] = TransporterProfileForm(**tkwargs)
            forms['truck_formset'] = TruckFormSet(
                post_data, instance=transporter, prefix='truck'
            ) if post_data is not None else TruckFormSet(instance=transporter, prefix='truck')

        return forms

    def get(self, request, pk, role_pk):
        party_role = self.get_party_role()
        return self.render(request, self.get_context(party_role))

    def post(self, request, pk, role_pk):
        party_role = self.get_party_role()
        forms = self.build_forms(party_role, post_data=request.POST, files=request.FILES)

        all_valid = all([
            forms['commercial_form'].is_valid(),
            forms['statutory_form'].is_valid(),
            forms['bank_formset'].is_valid(),
            forms['contact_formset'].is_valid(),
            forms['document_formset'].is_valid(),
        ])

        if party_role.role == PartyRoleType.VENDOR:
            all_valid = all_valid and forms['vendor_form'].is_valid()
        if party_role.role == PartyRoleType.TRANSPORTER:
            all_valid = all_valid and forms['transporter_form'].is_valid()
            all_valid = all_valid and forms['truck_formset'].is_valid()

        if not all_valid:
            messages.error(request, 'Please correct the errors below.')
            return self.render(request, self.get_context(party_role, forms))

        with transaction.atomic():
            user = request.user if request.user.is_authenticated else None
            commercial = forms['commercial_form'].save(commit=False)
            if user:
                commercial.updated_by = user
            commercial.save()

            statutory = forms['statutory_form'].save(commit=False)
            if user:
                statutory.updated_by = user
            statutory.save()

            bank_formset = forms['bank_formset']
            banks = bank_formset.save(commit=False)
            for bank in banks:
                if user:
                    bank.updated_by = user
                bank.save()
            for obj in bank_formset.deleted_objects:
                obj.delete()

            contact_formset = forms['contact_formset']
            contacts = contact_formset.save(commit=False)
            for contact in contacts:
                if user:
                    contact.updated_by = user
                contact.save()
            for obj in contact_formset.deleted_objects:
                obj.delete()

            document_formset = forms['document_formset']
            documents = document_formset.save(commit=False)
            for doc in documents:
                if user:
                    doc.updated_by = user
                doc.save()
            for obj in document_formset.deleted_objects:
                obj.delete()

            if party_role.role == PartyRoleType.VENDOR:
                vendor = forms['vendor_form'].save(commit=False)
                if user:
                    vendor.updated_by = user
                vendor.save()

            if party_role.role == PartyRoleType.TRANSPORTER:
                transporter = forms['transporter_form'].save(commit=False)
                if user:
                    transporter.updated_by = user
                transporter.save()
                truck_formset = forms['truck_formset']
                trucks = truck_formset.save(commit=False)
                for truck in trucks:
                    if user:
                        truck.updated_by = user
                    truck.save()
                for obj in truck_formset.deleted_objects:
                    obj.delete()

        messages.success(request, f'{party_role.get_role_display()} details saved successfully.')
        return redirect('parties:party_role_manage', pk=pk, role_pk=role_pk)

    def render(self, request, context):
        from django.shortcuts import render
        return render(request, self.template_name, context)


class PartyToggleActiveView(ERPLoginRequiredMixin, View):
    """Mark partner inactive or active (does not soft-delete)."""

    def post(self, request, pk):
        party = get_object_or_404(Party, pk=pk, is_deleted=False)
        if party.is_active:
            party.is_active = False
            party.save(update_fields=['is_active', 'updated_at'])
            messages.success(
                request,
                f'{party.code} — {party.name} deactivated.',
            )
        else:
            party.is_active = True
            party.save(update_fields=['is_active', 'updated_at'])
            messages.success(
                request,
                f'{party.code} — {party.name} activated.',
            )
        return redirect('parties:party_detail', pk=pk)


# Backward-compatible alias
PartySoftDeleteView = PartyToggleActiveView
