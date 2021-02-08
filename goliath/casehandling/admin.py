from django.contrib import admin
from django.db.models import Q
from django.utils.translation import gettext_lazy as _
from simple_history.admin import SimpleHistoryAdmin

from .models import (
    AutoreplyKeyword,
    Case,
    CaseType,
    Entity,
    ExternalSupport,
    ReceivedMessage,
    SentMessage,
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


class ApprovalFilter(admin.SimpleListFilter):
    """
    Instances deleted with django-simple-history are not shown it admin view.
    Make them visible via a list filter.
    """

    title = _("approval")
    parameter_name = "approval"

    def __init__(self, request, params, model, model_admin):
        super().__init__(request, params, model, model_admin)
        self.model = model

    def lookups(self, request, model_admin):
        return (
            ("needs_approval", _("needs approval")),
            ("was_approved", _("was approved")),
        )

    def queryset(self, request, queryset):
        if self.value() == "needs_approval":
            return queryset.filter(
                Q(case_type__needs_approval=True) & Q(approved_by=None)
            )
        if self.value() == "was_approved":
            return queryset.filter(
                Q(case_type__needs_approval=True) & ~Q(approved_by=None)
            )
        return queryset


class CaseAdmin(RemoveAdminAddButtonMixin, SimpleHistoryAdmin):
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
    list_filter = (ApprovalFilter, HistoryDeletedFilter)
    actions = ["aprove_case"]
    view_on_site = False

    def aprove_case(self, request, queryset):
        for case in queryset:
            case.approve_case(user=request.user)

    aprove_case.short_description = "Mark selected cases as approved"


class CaseTypeAdmin(HistoryDeletedFilterMixin, SimpleHistoryAdmin):
    list_display = [
        "id",
        "created_at",
        "name",
    ]
    view_on_site = False


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


class AutoreplyKeywordAdmin(HistoryDeletedFilterMixin, SimpleHistoryAdmin):
    view_on_site = False


admin.site.register(Entity, EntityAdmin)
admin.site.register(CaseType, CaseTypeAdmin)
admin.site.register(Case, CaseAdmin)
admin.site.register(ExternalSupport, ExternalSupportAdmin)
admin.site.register(ReceivedMessage, MessageAdmin)
admin.site.register(SentMessage, MessageAdmin)
admin.site.register(AutoreplyKeyword, AutoreplyKeywordAdmin)

# TODO: put into seperate app

from django.contrib import admin
from django.contrib.flatpages.admin import FlatPageAdmin
from django.contrib.flatpages.models import FlatPage

from .models import GoliathFlatPage


# Define a new FlatPageAdmin
class GoliathFlatPageAdmin(FlatPageAdmin):
    fieldsets = (
        (None, {"fields": ("url", "title", "content", "sites", "markdown_content")}),
        (
            _("Advanced options"),
            {
                "classes": ("collapse",),
                "fields": (
                    # "enable_comments",
                    "registration_required",
                    "template_name",
                ),
            },
        ),
    )


# Re-register FlatPageAdmin
admin.site.unregister(FlatPage)
admin.site.register(GoliathFlatPage, GoliathFlatPageAdmin)
