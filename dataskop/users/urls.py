from django.urls import include, path, re_path

from dataskop.users.views import (
    MagicLinkHandleConfirmationLink,
    MagicLinkHandleRegistrationLink,
    UserUpdate,
    export_text,
    magic_link_login_view,
)

urlpatterns = [
    path(
        "account/login/",
        magic_link_login_view,
        name="account_login_magic",
    ),
    path(
        "magic/login/",
        MagicLinkHandleConfirmationLink.as_view(),
        name="magic_login",
    ),
    path(
        "magic/registration/",
        MagicLinkHandleRegistrationLink.as_view(),
        name="magic_registration",
    ),
    path("account/", UserUpdate.as_view(), name="account_index"),
    path("export_text/", export_text, name="export_text"),
]
