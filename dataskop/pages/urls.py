from django.urls import path

from dataskop.campaigns.views import DonationListView
from dataskop.pages.views import HomePageView

urlpatterns = [
    path("", HomePageView.as_view(), name="home"),
]
