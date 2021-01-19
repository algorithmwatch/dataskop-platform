from django.contrib import admin
from django.contrib.auth import admin as auth_admin
from django.contrib.auth import get_user_model

from goliath.users.forms import UserChangeForm, UserCreationForm

User = get_user_model()


@admin.register(User)
class UserAdmin(auth_admin.UserAdmin):

    form = UserChangeForm
    add_form = UserCreationForm
    # fieldsets = (("User", {"fields": ("first_name", "last_name")}),) + tuple(
    #     auth_admin.UserAdmin.fieldsets
    # )
    list_display = ["first_name", "last_name", "is_superuser"]
    search_fields = ["first_name", "last_name"]
