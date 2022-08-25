from django.contrib import admin

from dataskop.lookups.models import Lookup


class LookupAdmin(admin.ModelAdmin):
    readonly_fields = ("created", "modified")
    search_fields = ("id",)
    list_filter = ("modified", "created", ("data", admin.EmptyFieldListFilter))
    list_display = ("modified", "created", "id")


admin.site.register(Lookup, LookupAdmin)
