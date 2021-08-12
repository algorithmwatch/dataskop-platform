import import_export
from allauth.account.models import EmailAddress
from django.contrib import admin
from django.contrib.admin import ModelAdmin
from django.contrib.auth import admin as auth_admin
from django.contrib.auth import get_user_model
from django.contrib.sessions.models import Session
from django.utils.translation import gettext_lazy as _

User = get_user_model()

# TODO: inline donations

# class PCCInline(admin.TabularInline):
#     model = PostCaseCreation


# class CaseInline(admin.TabularInline):
#     model = Case
#     fk_name = "user"


class UserResource(import_export.resources.ModelResource):
    class Meta:
        model = User
        fields = ("id", "email")


@admin.register(User)
class UserAdmin(import_export.admin.ExportMixin, auth_admin.UserAdmin):
    fieldsets = (
        (_("Personal info"), {"fields": ("first_name", "last_name", "email")}),
        (
            _("Permissions"),
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                ),
            },
        ),
        (_("Important dates"), {"fields": ("last_login", "date_joined")}),
    )
    list_display = [
        "email",
        "first_name",
        "last_name",
        "is_active",
        "is_superuser",
        "date_joined",
    ]
    search_fields = ["email", "first_name", "last_name"]
    ordering = ("-date_joined",)
    # inlines = [PCCInline, CaseInline]

    resource_class = UserResource
    formats = [
        import_export.formats.base_formats.JSON,
    ]

    # only return users with primary, verified email address
    def get_export_queryset(self, request):

        verified_emails = EmailAddress.objects.filter(verified=True).values_list(
            "email", flat=True
        )

        return (
            super(UserAdmin, self)
            .get_export_queryset(request)
            .filter(email__in=verified_emails)
        )

    def has_add_permission(self, request, obj=None):
        return False


class SessionAdmin(ModelAdmin):
    def _session_data(self, obj):
        return obj.get_decoded()

    list_display = ["session_key", "_session_data", "expire_date"]
    readonly_fields = ["session_key", "_session_data", "expire_date"]
    exclude = ["session_data"]
    date_hierarchy = "expire_date"


admin.site.register(Session, SessionAdmin)
