from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from django.views.generic.list import ListView

from dataskop.campaigns.models import Donation


@method_decorator(never_cache, name="dispatch")
class DonationListView(LoginRequiredMixin, ListView):
    model = Donation
    template_name = "campaigns/donation_list.html"

    def get_queryset(self):
        """
        limit to user
        """
        qs = Donation.objects.filter(user=self.request.user)
        return qs
