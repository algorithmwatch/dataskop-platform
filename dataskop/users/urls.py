from django.urls import include, path, re_path

from dataskop.users.views import (
    MagicLinkLoginEmail,
    MagicLinkVerifyEmail,
    UserUpdate,
    export_text,
    magic_link_login_view,
)

urlpatterns = [
    path("export_text/", export_text, name="export_text"),
    path(
        "magic/registration/",
        MagicLinkVerifyEmail.as_view(),
        name="magic_registration",
    ),
    path(
        "magic/login/",
        MagicLinkLoginEmail.as_view(),
        name="magic_login",
    ),
    path(
        "account/login/magic/",
        magic_link_login_view,
        name="account_login_magic",
    ),
    path("account/", UserUpdate.as_view(), name="account_index"),
]
