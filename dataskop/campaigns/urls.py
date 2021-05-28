from django.urls import path

from dataskop.campaigns.views import DonationListView

urlpatterns = [
    path("spenden/", DonationListView.as_view(), name="donation-list"),
]
