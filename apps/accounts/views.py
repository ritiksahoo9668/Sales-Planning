from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import RedirectView


class DashboardRedirectView(LoginRequiredMixin, RedirectView):
    pattern_name = 'parties:party_list'
    permanent = False
