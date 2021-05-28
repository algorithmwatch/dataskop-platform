from django.contrib import admin
from guardian.admin import GuardedModelAdmin

from .models import Campaign, Donation


class CampaignAdmin(GuardedModelAdmin):
    prepopulated_fields = {"slug": ("title",)}
    list_display = ("title", "slug", "created")
    search_fields = ("title", "content")
    ordering = ("-created",)
    date_hierarchy = "created"


admin.site.register(Campaign, CampaignAdmin)
