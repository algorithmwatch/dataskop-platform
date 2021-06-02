from django.urls import path

from dataskop.campaigns.views import (
    DonationDeleteView,
    DonationDetailView,
    DonationListView,
    DonationUnconfirmedView,
)

urlpatterns = [
    path("meine-spenden/", DonationListView.as_view(), name="my-donations-list"),
    path(
        "meine-spenden-unbestaetigt/",
        DonationUnconfirmedView.as_view(),
        name="my-donations-unconfirmed",
    ),
    path(
        "meine-spenden/<int:pk>/",
        DonationDetailView.as_view(),
        name="my-donations-detail",
    ),
    path(
        "meine-spenden-loeschen/<int:pk>/",
        DonationDeleteView.as_view(),
        name="my-donations-delete",
    ),
]
