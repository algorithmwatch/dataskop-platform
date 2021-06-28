from django.conf import settings
from rest_framework.routers import DefaultRouter, SimpleRouter

from dataskop.campaigns.api.views import (
    CampaignViewSet,
    DonationUnauthorizedViewSet,
    EventViewSet,
)

if settings.DEBUG:
    router = DefaultRouter()
else:
    router = SimpleRouter()

router.register("donate", DonationUnauthorizedViewSet, "donate")
router.register("campaigns", CampaignViewSet, "campaigns")
router.register("events", EventViewSet, "events")


app_name = "api"
urlpatterns = router.urls
