from django.urls import path

from dataskop.campaigns.views import (
    DashboardView,
    DonationDeleteView,
    DonationDetailDownloadView,
    DonationDetailView,
    DonationDownloadAllView,
    DonationListView,
    DonationUnconfirmedView,
    DonorNotificationDisableView,
    DonorNotificationSettingUpdateView,
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
        DonationDownloadAllView.as_view(),
        name="download_all",
    ),
    path(
        "benachrichtigungen/",
        DonorNotificationSettingUpdateView.as_view(),
        name="donor_notification_setting",
    ),
    path(
        "benachrichtigungen-abbestellen/",
        DonorNotificationDisableView.as_view(),
        name="donor_notification_disable",
    ),
    path("dashboard/", DashboardView.as_view(), name="dashboard"),
]
