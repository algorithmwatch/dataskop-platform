from datetime import timedelta
from functools import cached_property

from allauth.account.models import EmailAddress
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.core.exceptions import PermissionDenied
from django.db.models import Count, Value
from django.db.models.fields import CharField
from django.db.models.functions.datetime import TruncDay
from django.http.response import JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.utils.text import slugify
from django.views.decorators.cache import never_cache
from django.views.generic import DetailView, ListView, View
from django.views.generic.edit import DeleteView, FormView, UpdateView
from sesame.utils import get_user

from dataskop.campaigns.forms import (
    DashboardForm,
    DonorNotificationDisableForm,
    DonorNotificationSettingForm,
)
from dataskop.campaigns.models import (
    Campaign,
    Donation,
    DonorNotificationSetting,
    Event,
)
from dataskop.users.models import User


class UsersDonationMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        obj = self.get_object()  # type: ignore
        return obj.donor == self.request.user or self.request.user.is_staff  # type: ignore


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
        context["num_unconfirmed_donations"] = Donation.objects.unconfirmed_by_user(
            self.request.user
        ).count()
        return context


@method_decorator(never_cache, name="dispatch")
class DonationUnconfirmedListView(LoginRequiredMixin, ListView):
    model = Donation
    template_name = "campaigns/donation_unconfirmed_list.html"

    def get_queryset(self):
        return Donation.objects.unconfirmed_by_user(self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["hide_title"] = True
        return super().get_context_data(**kwargs)


@method_decorator(never_cache, name="dispatch")
class DonationUnconfirmedView(LoginRequiredMixin, View):
    def post(self, request):
        for d in Donation.objects.unconfirmed_by_user(request.user):
            d.confirm(request.user)
        return redirect("my_donations_unconfirmed")

    def get(self, request, *args, **kwargs):
        view = DonationUnconfirmedListView.as_view()
        return view(request, *args, **kwargs)


class DonationDetailViewGet(UsersDonationMixin, DetailView):
    model = Donation


class DonationDetailDownloadView(DonationDetailViewGet):
    def render_to_response(self, context, **response_kwargs):
        response = JsonResponse({"results": context["object"].results})
        response[
            "Content-Disposition"
        ] = f"attachment; filename=dataskop-export-{context['object'].id}.json"
        return response


class DonationDownloadAllView(LoginRequiredMixin, View):
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
    success_url = reverse_lazy("my_donations_list")
    success_message = "Die Spende wurde erfolgreich gelöscht."

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        obj = self.get_object()
        # Create the event in the view to only catch deletion requested from users.
        Event.objects.create(
            message=f"donation deleted",
            data={"donation": obj.pk, "user": obj.donor.pk},
            campaign=obj.campaign,
        )
        return super(DonationDeleteView, self).delete(request, *args, **kwargs)


@method_decorator(never_cache, name="dispatch")
class DonationDetailView(View):
    def get(self, request, *args, **kwargs):
        view = DonationDetailViewGet.as_view()
        return view(request, *args, **kwargs)


@method_decorator(never_cache, name="dispatch")
class DonorNotificationSettingUpdateView(LoginRequiredMixin, UpdateView):
    model = DonorNotificationSetting
    form_class = DonorNotificationSettingForm
    success_url = reverse_lazy("donor_notification_setting")

    def get_object(self):
        user = self.request.user
        obj, created = DonorNotificationSetting.objects.get_or_create(user=user)
        return obj


class DonorNotificationDisableView(SuccessMessageMixin, FormView):
    template_name = "campaigns/donornotificationsetting_disable.html"
    form_class = DonorNotificationDisableForm
    success_url = reverse_lazy("home")
    success_message = "Die Einstellung wurde erfolgreich übernommen."

    def get_user_campaign(self, with_user=False):
        """
        Weird handling of the `request` / `with_user`, FIXME.
        """
        campaign_pk = self.request.GET.get("c")
        if campaign_pk is None:
            raise PermissionDenied()

        campaign = Campaign.objects.filter(pk=int(campaign_pk)).first()
        if campaign is None:
            raise PermissionDenied()

        user = (
            get_user(
                self.request,
                scope=f"disable-notification-{campaign_pk}",
                max_age=timedelta(days=90),
            )
            if with_user
            else None
        )
        return user, campaign

    def get_context_data(self, **kwargs):
        context = super(DonorNotificationDisableView, self).get_context_data(**kwargs)
        _, campaign = self.get_user_campaign()
        context["campaign_title"] = campaign and campaign.title
        return context

    def form_valid(self, form):
        user, campaign = self.get_user_campaign(True)

        if user is None:
            messages.error(
                self.request, "Es gab einen Fehler, bitte nochmals einloggen."
            )
            # Something went wrong (maybe Redis was cleared?) so redirect to proper settings page.
            return redirect("donor_notification_setting")

        settings, _ = DonorNotificationSetting.objects.get_or_create(user=user)
        if form.cleaned_data["disable"]:
            settings.disabled_campaigns.add(campaign)
        else:
            settings.disabled_campaigns.remove(campaign)

        return super().form_valid(form)


@method_decorator(
    staff_member_required(login_url=reverse_lazy("magic_login")), name="dispatch"
)
class DashboardView(FormView):
    """
    A staff-only view to see statistics about campaigns. You need to select a single
    campaign.
    """

    form_class = DashboardForm
    template_name = "campaigns/dashboard.html"

    @cached_property
    def campaign(self):
        return get_object_or_404(
            Campaign, pk=self.request.GET.get("campaign", Campaign.objects.last().pk)
        )

    def get_initial(self):
        return {**super().get_initial(), "campaign": self.campaign}

    def get_context_data(self, **kwargs):
        context = super(DashboardView, self).get_context_data(**kwargs)

        context["num_donations"] = self.campaign.donation_set.count()
        context["num_donations_distinct"] = self.campaign.donation_set.distinct(
            "donor"
        ).count()

        # Get total number of events and also aggregate per day
        qs = Event.objects.filter(campaign=self.campaign)
        msgs = qs.order_by().values_list("message", flat=True).distinct()
        context["events"] = {}
        context["total_events"] = {}

        for m in msgs:
            context["events"][m] = (
                qs.filter(message=m)
                .annotate(date_histogram=TruncDay("created"))
                .values("date_histogram")
                .order_by("date_histogram")
                .annotate(
                    total=Count("date_histogram"),
                    time_interval=Value("day", CharField()),
                )
            )

        for m in msgs:
            context["total_events"][m] = qs.filter(message=m).count()

        # Get all users that deleted their account and also donated to the given campaign.
        context["user_deleted"] = []
        for event in Event.objects.filter(message="user deleted").values():
            if any(
                [
                    d["campaign"] == self.campaign.pk
                    for d in event["data"].get("donations", [])
                ]
            ):
                context["user_deleted"].append(event)

        return context
