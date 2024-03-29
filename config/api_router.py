from django.conf import settings
from rest_framework.routers import DefaultRouter, SimpleRouter

from dataskop.campaigns.api.views import (
    CampaignViewSet,
    DonationUnauthorizedViewSet,
    EventViewSet,
)
from dataskop.lookups.api.views import LookupJobViewSet, PublicLookupViewSet
from dataskop.mailjetsync.api.views import NewsletterSubcriptionViewSet

if settings.DEBUG:
    router = DefaultRouter()
else:
    router = SimpleRouter()

router.register("donations", DonationUnauthorizedViewSet, "donations")
router.register("campaigns", CampaignViewSet, "campaigns")
router.register("events", EventViewSet, "events")
router.register("lookups", PublicLookupViewSet, "lookups")
router.register("lookupjobs", LookupJobViewSet, "lookupjobs")
router.register("mailjetsync", NewsletterSubcriptionViewSet, "mailjetsync")


app_name = "api"
urlpatterns = router.urls
