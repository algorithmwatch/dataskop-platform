from allauth.account.models import EmailAddress
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.http.response import JsonResponse
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.utils.text import slugify
from django.views.decorators.cache import never_cache
from django.views.generic import DetailView, ListView, View
from django.views.generic.edit import DeleteView

from dataskop.campaigns.models import Donation

User = get_user_model()


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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context[
            "num_unconfirmed_donations"
        ] = Donation.objects.unconfirmed_donations_by_user(self.request.user).count()
        return context


@method_decorator(never_cache, name="dispatch")
class DonationUnconfirmedListView(LoginRequiredMixin, ListView):
    model = Donation
    template_name = "campaigns/donation_unconfirmed_list.html"

    def get_queryset(self):
        return Donation.objects.unconfirmed_donations_by_user(self.request.user)


@method_decorator(never_cache, name="dispatch")
class DonationUnconfirmedView(LoginRequiredMixin, View):
    def post(self, request):
        Donation.objects.unconfirmed_donations_by_user(request.user).update(
            donor=request.user
        )
        return redirect("my-donations-unconfirmed")

    def get(self, request, *args, **kwargs):
        view = DonationUnconfirmedListView.as_view()
        return view(request, *args, **kwargs)


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


class DonationDetailDownloadView(DonationDetailViewGet):
    def render_to_response(self, context, **response_kwargs):
        response = JsonResponse({"results": context["object"].results})
        response[
            "Content-Disposition"
        ] = f"attachment; filename=dataskop-export-{context['object'].id}.json"
        return response


class DonationDownloadAll(LoginRequiredMixin, View):
    def get(self, request):
        export = {}
        export["user"] = list(User.objects.filter(email=request.user.email).values())
        export["emails"] = list(EmailAddress.objects.filter(user=request.user).values())
        export["donations"] = list(Donation.objects.filter(donor=request.user).values())

        response = JsonResponse(export)
        response[
            "Content-Disposition"
        ] = f"attachment; filename=dataskop-export-{slugify(request.user.email)}.json"
        return response


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
