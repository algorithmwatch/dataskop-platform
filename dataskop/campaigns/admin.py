import import_export
from allauth.account.models import EmailAddress
from django.contrib import admin, messages
from django.template.response import TemplateResponse
from django.utils.translation import ngettext

from .models import (
    Campaign,
    Donation,
    DonorNotification,
    DonorNotificationSetting,
    Event,
    Provider,
    SiteExtended,
)

admin.site.register(Provider)
admin.site.register(SiteExtended)


class CampaignAdmin(admin.ModelAdmin):
    list_display = ("title", "slug", "created")
    search_fields = ("title", "content")
    ordering = ("-created",)
    date_hierarchy = "created"


admin.site.register(Campaign, CampaignAdmin)


class DonorNotificationSettingAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "disable_all",
    )
    search_fields = ("user__first_name", "user__last_name", "user__email")


admin.site.register(DonorNotificationSetting, DonorNotificationSettingAdmin)


class DonorNotificationAdmin(admin.ModelAdmin):
    list_display = (
        "subject",
        "campaign",
        "created",
        "sent_by",
        "draft",
    )
    search_fields = ("subject", "text")

    def has_change_permission(self, request, obj=None):
        """
        The notification can't be updated if the emails were already sent.
        """
        return obj and obj.draft

    def get_form(self, request, obj=None, **kwargs):
        form = super(DonorNotificationAdmin, self).get_form(request, obj, **kwargs)

        # If the mail was sent, don't manipulate the form.
        if obj and not obj.draft:
            return form

        sent_by_field = form.base_fields["sent_by"]
        campaign_field = form.base_fields["campaign"]
        sent_by_field.initial = request.user
        sent_by_field.disabled = True
        for f in [campaign_field, sent_by_field]:
            f.widget.can_add_related = False
            f.widget.can_change_related = False
            f.widget.can_delete_related = False

        return form


admin.site.register(DonorNotification, DonorNotificationAdmin)


class EventAdmin(admin.ModelAdmin):
    list_display = ("campaign", "message", "created")
    list_filter = ("campaign", "message", "created")
    search_fields = ("message",)
    ordering = ("-created",)
    date_hierarchy = "created"
    list_per_page = 1000


admin.site.register(Event, EventAdmin)


class DonationResultsWidget:
    """
    We have to define our own Widget to avoid escaping the JSON with the default
    JSONWidget.
    """

    def clean(self, value, row=None, **kwargs):
        return value

    def render(self, value, obj=None):
        return value.results


class DonationResource(import_export.resources.ModelResource):
    results = import_export.fields.Field(
        attribute="results", widget=DonationResultsWidget
    )

    class Meta:
        model = Donation
        exclude = ("ip_address", "unauthorized_email")


def send_reminder_to_confirm(modeladmin, request, queryset):
    """
    Remind users to verify their email address in order to confirm their donations.
    For the users in the queryset, that already had their email address confirmed, do
    nothing.
    """
    num_sent = Donation.objects.remind_user_registration(donation_qs=queryset)

    modeladmin.message_user(
        request,
        ngettext(
            "%d reminder was sent",
            "%d reminders were sent.",
            num_sent,
        )
        % num_sent,
        messages.INFO,
    )


def dry_run_send_reminder_to_confirm(modeladmin, request, queryset):
    """
    Remind users to verify their email address in order to confirm their donations.
    For the users in the queryset, that already had their email address confirmed, do
    nothing.
    """
    num_sent = Donation.objects.remind_user_registration(
        donation_qs=queryset, dryrun=True
    )

    modeladmin.message_user(
        request,
        ngettext(
            "DRY RUN: %d reminder was sent",
            "DRY RUN: %d reminders were sent.",
            num_sent,
        )
        % num_sent,
        messages.INFO,
    )


def require_confirmation(func):
    """
    Decorator to confirm an (possibly destructive) admin action.
    """

    def wrapper(modeladmin, request, queryset):
        if request.POST.get("confirmation") is None:
            request.current_app = modeladmin.admin_site.name
            context = {"action": request.POST["action"], "queryset": queryset}
            return TemplateResponse(request, "admin/action_confirmation.html", context)

        return func(modeladmin, request, queryset)

    wrapper.__name__ = func.__name__
    return wrapper


@require_confirmation
def delete_unconfirmed_donations(modeladmin, request, queryset):
    del_objcts = Donation.objects.delete_unconfirmed_donations(donation_qs=queryset)

    modeladmin.message_user(
        request,
        "deleted: " + str(del_objcts.items()),
        messages.INFO,
    )


def dry_run_delete_unconfirmed_donations(modeladmin, request, queryset):
    del_objcts = Donation.objects.delete_unconfirmed_donations(
        donation_qs=queryset, dryrun=True
    )

    modeladmin.message_user(
        request,
        "DRY RUN: deleted: " + str(del_objcts.items()),
        messages.INFO,
    )


@admin.action(description="Manually mark donations as confirmed")
def confirm_donations(modeladmin, request, queryset):
    confirmed = []
    for donation in queryset.unconfirmed():
        email_obj = EmailAddress.objects.filter(
            email=donation.unauthorized_email
        ).first()
        if email_obj is None:
            continue
        donation.confirm(email_obj.user, send_email=True)
        confirmed.append(donation.pk)

    if len(confirmed) > 0:
        Event.objects.create(
            message="Manually marked some donations as confirmed",
            data={"pks": confirmed},
        )

    modeladmin.message_user(
        request,
        f"Manually marked {len(confirmed)} donation(s) as confirmed",
        messages.INFO,
    )


class UnconfirmedDonationsFilter(admin.SimpleListFilter):
    """
    Filter for (un)confirmed donations by checking if the user is verified.
    """

    title = "confirmed"
    parameter_name = "confirmed"

    def lookups(self, request, model_admin):
        return (("confirmed", "Confirmed"), ("unconfirmed", "Unconfirmed"))

    def queryset(self, request, queryset):
        val = self.value()
        if val is None:
            return queryset
        elif val.lower() == "confirmed":
            return queryset.confirmed()
        elif val.lower() == "unconfirmed":
            return queryset.unconfirmed()


class DonationAdmin(import_export.admin.ExportMixin, admin.ModelAdmin):
    readonly_fields = (
        "created",
        "modified",
    )
    search_fields = ["unauthorized_email", "donor__email"]
    list_filter = ("campaign", "created", UnconfirmedDonationsFilter)
    list_display = ("campaign", "created", "unauthorized_email", "donor")

    actions = [
        confirm_donations,
        send_reminder_to_confirm,
        delete_unconfirmed_donations,
        dry_run_send_reminder_to_confirm,
        dry_run_delete_unconfirmed_donations,
    ]

    resource_class = DonationResource
    formats = [
        import_export.formats.base_formats.JSON,
    ]

    # only return donaions from verified users
    def get_export_queryset(self, request):
        return (
            super(DonationAdmin, self)
            .get_export_queryset(request)
            .filter(donor__isnull=False)
            .select_related()
        )


admin.site.register(Donation, DonationAdmin)
