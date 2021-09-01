import import_export
from django.contrib import admin
from django.db.models import JSONField
from guardian.admin import GuardedModelAdmin
from jsoneditor.forms import JSONEditor

from .models import Campaign, Donation, Event, Provider

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


def admin_sent_reminder(modeladmin, request, queryset):
    Donation.objects.remind_user_registration(donation_qs=queryset)


admin_sent_reminder.short_description = "Sent reminders for registration"


class DonationAdmin(import_export.admin.ExportMixin, admin.ModelAdmin):
    search_fields = ["unauthorized_email", "donor__email"]
    actions = [admin_sent_reminder]

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
