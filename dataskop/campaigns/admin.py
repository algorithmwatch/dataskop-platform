from django.contrib import admin
from django.db.models import JSONField
from guardian.admin import GuardedModelAdmin
from jsoneditor.forms import JSONEditor

from .models import Campaign, Donation, Event, Provider


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

admin.site.register(Provider)
admin.site.register(Donation)
