from django.urls import path

from dataskop.campaigns.views import (
    DonationDeleteView,
    DonationDetailDownloadView,
    DonationDetailView,
    DonationDownloadAll,
    DonationListView,
    DonationUnconfirmedView,
)

urlpatterns = [
    path("meine-spenden/", DonationListView.as_view(), name="my_donations_list"),
    path(
        "meine-spenden-unbestaetigt/",
        DonationUnconfirmedView.as_view(),
        name="my_donations_unconfirmed",
    ),
    path(
        "meine-spenden/<int:pk>/",
        DonationDetailView.as_view(),
        name="my_donations_detail",
    ),
    path(
        "meine-spenden-loeschen/<int:pk>/",
        DonationDeleteView.as_view(),
        name="my_donations_delete",
    ),
    path(
        "meine-spenden-download/<int:pk>/",
        DonationDetailDownloadView.as_view(),
        name="my_donations_download",
    ),
    path(
        "download-all/",
        DonationDownloadAll.as_view(),
        name="download_all",
    ),
]
