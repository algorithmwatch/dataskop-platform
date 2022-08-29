from django.contrib import admin

from dataskop.lookups.models import Lookup, LookupJob


class LookupAdmin(admin.ModelAdmin):
    readonly_fields = ("created", "modified")
    search_fields = ("id",)
    list_filter = (
        "modified",
        "created",
    )
    list_display = ("modified", "created", "id")


admin.site.register(Lookup, LookupAdmin)


class LookupJobAdmin(admin.ModelAdmin):
    readonly_fields = ("created", "modified")
    search_fields = ("log", "user")
    list_filter = (
        "modified",
        "created",
        "processing",
        "error",
        "done",
        "trusted",
        ("input_todo", admin.EmptyFieldListFilter),
        ("input_done", admin.EmptyFieldListFilter),
    )
    list_display = ("modified", "created", "processing", "done", "error")


admin.site.register(LookupJob, LookupJobAdmin)
