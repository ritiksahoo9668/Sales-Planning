from django.contrib.auth.mixins import LoginRequiredMixin


class ERPLoginRequiredMixin(LoginRequiredMixin):
    pass


class AuditMixin:
    """Set created_by / updated_by on save from request user."""

    def form_valid(self, form):
        user = getattr(self.request, 'user', None)
        if user and user.is_authenticated:
            if not form.instance.pk and hasattr(form.instance, 'created_by'):
                form.instance.created_by = user
            if hasattr(form.instance, 'updated_by'):
                form.instance.updated_by = user
        return super().form_valid(form)
