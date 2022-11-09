from django.urls import path

from dataskop.mailjetsync.views import MailjetSyncConfirmationLink

urlpatterns = [
    path(
        "mailjet/magic/confirm/",
        MailjetSyncConfirmationLink.as_view(),
        name="mailjet_magic_confirm",
    ),
]
