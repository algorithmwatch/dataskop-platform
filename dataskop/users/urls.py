from django.urls import path

from dataskop.users.views import (
    MagicLinkFormView,
    MagicLinkHandleConfirmationLink,
    MagicLinkHandleRegistrationLink,
    UserDeleteView,
    UserUpdateView,
)

urlpatterns = [
    path(
        "magic/login/",
        MagicLinkFormView.as_view(),
        name="magic_login",
    ),
    path(
        "magic/confirm/",
        MagicLinkHandleConfirmationLink.as_view(),
        name="magic_confirm",
    ),
    path(
        "magic/registration/",
        MagicLinkHandleRegistrationLink.as_view(),
        name="magic_registration",
    ),
    path("account/", UserUpdateView.as_view(), name="account_index"),
    path("account/delete/", UserDeleteView.as_view(), name="account_delete"),
]
