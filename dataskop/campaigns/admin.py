import import_export
from django.contrib import admin, messages
from django.db.models import JSONField
from django.template.response import TemplateResponse
from django.utils.translation import ngettext
from guardian.admin import GuardedModelAdmin
from jsoneditor.forms import JSONEditor

from .models import (
    Campaign,
    Donation,
    DonorNotification,
    DonorNotificationSetting,
    Event,
    Provider,
)

admin.site.register(Provider)


class TextJSONEditor(JSONEditor):
    jsoneditor_options = {"mode": "text"}


class CampaignAdmin(GuardedModelAdmin):
    list_display = ("title", "slug", "created")
    search_fields = ("title", "content")
    ordering = ("-created",)
    date_hierarchy = "created"

    formfield_overrides = {JSONField: {"widget": TextJSONEditor}}


admin.site.register(Campaign, CampaignAdmin)


class DonorNotificationSettingAdmin(GuardedModelAdmin):
    list_display = (
        "user",
        "disable_all",
    )
    search_fields = ("user__first_name", "user__last_name", "user__email")


admin.site.register(DonorNotificationSetting, DonorNotificationSettingAdmin)


class DonorNotificationAdmin(GuardedModelAdmin):
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


class EventAdmin(GuardedModelAdmin):
    list_display = ("campaign", "message", "created")
    search_fields = ("message",)
    ordering = ("-created",)
    date_hierarchy = "created"


admin.site.register(Event, EventAdmin)


class DonationResource(import_export.resources.ModelResource):
    class Meta:
        model = Donation
        exclude = ("ip_address", "unauthorized_email")


def admin_send_reminder(modeladmin, request, queryset):
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


admin_send_reminder.short_description = "Send reminders to unverified donations"


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


class UnconfirmedDonationsFilter(admin.SimpleListFilter):
    """
    Filter for (un)confirmed donations by checking if the user is verified.
    """

    title = "confirmed"
    parameter_name = "confirmed"

    def lookups(self, request, model_admin):
        return (("confirmed", "Confirmed"), ("unconfirmed", "Unconfirmed"))

    def queryset(self, request, queryset):
        if not self.value():
            return queryset
        if self.value().lower() == "confirmed":
            return queryset.filter(donor__isnull=False)
        elif self.value().lower() == "unconfirmed":
            return queryset.filter(donor__isnull=True)


class DonationAdmin(import_export.admin.ExportMixin, admin.ModelAdmin):
    readonly_fields = (
        "created",
        "modified",
    )
    search_fields = ["unauthorized_email", "donor__email"]
    list_filter = ("campaign", "created", UnconfirmedDonationsFilter)
    list_display = ("campaign", "created", "unauthorized_email", "donor")

    actions = [admin_send_reminder, delete_unconfirmed_donations]

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
