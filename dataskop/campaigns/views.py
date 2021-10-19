from datetime import timedelta

from allauth.account.models import EmailAddress
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.core.exceptions import PermissionDenied
from django.db.models import Count, Value
from django.db.models.fields import CharField
from django.db.models.functions.datetime import TruncDay
from django.http.response import JsonResponse
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.utils.text import slugify
from django.views.decorators.cache import never_cache
from django.views.generic import DetailView, ListView, View
from django.views.generic.base import TemplateView
from django.views.generic.edit import DeleteView, FormView, UpdateView
from sesame.utils import get_user

from dataskop.campaigns.forms import (
    DonorNotificationDisableForm,
    DonorNotificationSettingForm,
)
from dataskop.campaigns.models import (
    Campaign,
    Donation,
    DonorNotificationSetting,
    Event,
)

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


@method_decorator(never_cache, name="dispatch")
class DonationUnconfirmedView(LoginRequiredMixin, View):
    def post(self, request):
        Donation.objects.unconfirmed_by_user(request.user).update(donor=request.user)
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
        Event.objects.create(
            message=f"donation deleted: {self.get_object().pk}",
            campaign=self.get_object().campaign,
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

    def get_user_campaing(self, with_user=False):
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
        _, campaign = self.get_user_campaing()
        context["campaign_title"] = campaign and campaign.title
        return context

    def form_valid(self, form):
        user, campaign = self.get_user_campaing(True)

        if user is None:
            messages.error(self.request, "Es gab ein Fehler, bitte nochmals einloggen.")
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
class DashboardView(TemplateView):
    template_name = "campaigns/dashboard.html"

    def get_context_data(self, **kwargs):
        context = super(DashboardView, self).get_context_data(**kwargs)

        msgs = Event.objects.order_by().values_list("message", flat=True).distinct()

        # group special events (that have some identifier in the name)
        msg_fixed = []
        for m in msgs:
            if m is None:
                continue

            if "user deleted:" in m:
                msg_fixed.append("user deleted")
            elif "donation deleted" in m:
                msg_fixed.append("donation deleted")
            elif "user was logged out" in m:
                msg_fixed.append("user was logged out")
            else:
                msg_fixed.append(m)

        msgs = list(set(msg_fixed))

        context["events"] = {}
        context["total_events"] = {}

        for m in msgs:
            context["events"][m] = (
                Event.objects.filter(message__icontains=m)
                .annotate(date_histogram=TruncDay("created"))
                .values("date_histogram")
                .order_by("date_histogram")
                .annotate(
                    total=Count("date_histogram"),
                    time_interval=Value("day", CharField()),
                )
            )

        for m in msgs:
            context["total_events"][m] = Event.objects.filter(
                message__icontains=m
            ).count()

        return context
