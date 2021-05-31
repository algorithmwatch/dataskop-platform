from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from django.views.generic import DetailView, ListView, View
from django.views.generic.edit import DeleteView

from dataskop.campaigns.models import Donation


class UsersDonationMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        obj = self.get_object()
        return obj.donor == self.request.user or self.request.user.is_staff


@method_decorator(never_cache, name="dispatch")
class DonationListView(LoginRequiredMixin, ListView):
    model = Donation

    def get_queryset(self):
        """
        limit to user
        """
        qs = Donation.objects.filter(donor=self.request.user)
        return qs


# class CaseStatusUpdateView(LoginRequiredMixin,UsersDonationMixin, UpdateView):
#     template_name = "casehandling/case_detail.html"
#     form_class = CaseStatusForm
#     model = Donation

#     def get_success_url(self):
#         return self.object.get_absolute_url()

#     def test_func(self):
#         obj = self.get_object()
#         return obj.user == self.request.user or self.request.user.is_staff


class DonationDetailViewGet(UsersDonationMixin, DetailView):
    model = Donation

    # def get_context_data(self, **kwargs):
    #     context = super().get_context_data(**kwargs)
    #     context["form"] = CaseStatusForm()
    #     return context


# can't use SuccessMessageMixin https://stackoverflow.com/a/25325228/4028896
class DonationDeleteView(UsersDonationMixin, DeleteView):
    model = Donation
    success_url = reverse_lazy("my-donations-list")
    success_message = "Die Spende wurde erfolgreich gelöscht."

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super(DonationDeleteView, self).delete(request, *args, **kwargs)


@method_decorator(never_cache, name="dispatch")
class DonationDetailView(View):
    def get(self, request, *args, **kwargs):
        view = DonationDetailViewGet.as_view()
        return view(request, *args, **kwargs)

    # def post(self, request, *args, **kwargs):
    #     view = CaseStatusUpdateView.as_view()
    #     return view(request, *args, **kwargs)
