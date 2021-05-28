from django.contrib import admin
from django.contrib.auth import admin as auth_admin
from django.contrib.auth import get_user_model
from django.utils.translation import gettext
from django.utils.translation import gettext_lazy as _

User = get_user_model()

# TODO: inline donations

# class PCCInline(admin.TabularInline):
#     model = PostCaseCreation


# class CaseInline(admin.TabularInline):
#     model = Case
#     fk_name = "user"


@admin.register(User)
class UserAdmin(auth_admin.UserAdmin):
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

    def has_add_permission(self, request, obj=None):
        return False
