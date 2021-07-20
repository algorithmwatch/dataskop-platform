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


class DonationAdmin(import_export.admin.ExportMixin, admin.ModelAdmin):
    resource_class = DonationResource
    formats = [
        import_export.formats.base_formats.JSON,
    ]

    # only return verified users
    def get_export_queryset(self, request):
        return (
            super(DonationAdmin, self)
            .get_export_queryset(request)
            .filter(donor__isnull=False)
        )


admin.site.register(Donation, DonationAdmin)
