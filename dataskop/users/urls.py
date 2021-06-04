from django.urls import path

from dataskop.users.views import (
    MagicLinkHandleConfirmationLink,
    MagicLinkHandleRegistrationLink,
    UserDeleteView,
    UserUpdateView,
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
    path("account/", UserUpdateView.as_view(), name="account_index"),
    path("account/delete/", UserDeleteView.as_view(), name="account_delete"),
]
