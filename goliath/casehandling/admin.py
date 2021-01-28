from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin
from django.utils.translation import gettext_lazy as _


from .models import (
    Case,
    CaseType,
    Entity,
    MessageReceived,
    MessageSent,
    ExternalSupport,
)


class RemoveAdminAddButtonMixin(object):
    def has_add_permission(self, request, obj=None):
        return False


class HistoryDeletedFilter(admin.SimpleListFilter):
    """
    Instances deleted with django-simple-history are not shown it admin view.
    Make them visible via a list filter.
    """

    title = _("deleted")
    parameter_name = "is_deleted"

    def __init__(self, request, params, model, model_admin):
        super().__init__(request, params, model, model_admin)
        self.model = model

    def lookups(self, request, model_admin):
        return (("deleted", _("deleted")),)

    def queryset(self, request, queryset):
        if self.value() == "deleted":
            return queryset.union(self.model.history.filter(history_type="-"))
        return queryset


class HistoryDeletedFilterMixin(object):
    list_filter = (HistoryDeletedFilter,)


class CaseAdmin(
    RemoveAdminAddButtonMixin, HistoryDeletedFilterMixin, SimpleHistoryAdmin
):
    list_display = [
        "id",
        "created_at",
        "status",
        "case_type",
        "user",
        "email",
    ]
    search_fields = [
        "answers_text",
        "user__first_name",
        "user__last_name",
        "user__email",
    ]


class CaseTypeAdmin(HistoryDeletedFilterMixin, SimpleHistoryAdmin):
    list_display = [
        "id",
        "created_at",
        "name",
        "entity",
    ]


class EntityAdmin(HistoryDeletedFilterMixin, SimpleHistoryAdmin):
    list_display = [
        "id",
        "created_at",
        "name",
        "email",
        "url",
    ]


class MessageAdmin(
    RemoveAdminAddButtonMixin, HistoryDeletedFilterMixin, SimpleHistoryAdmin
):
    list_display = ["id", "created_at", "subject", "from_email", "to_email"]


class ExternalSupportAdmin(HistoryDeletedFilterMixin, SimpleHistoryAdmin):
    list_display = [
        "id",
        "created_at",
        "name",
        "url",
    ]


admin.site.register(Entity, EntityAdmin)
admin.site.register(CaseType, CaseTypeAdmin)
admin.site.register(Case, CaseAdmin)
admin.site.register(ExternalSupport, ExternalSupportAdmin)
admin.site.register(MessageReceived, MessageAdmin)
admin.site.register(MessageSent, MessageAdmin)
