from django.conf import settings
from rest_framework.routers import DefaultRouter, SimpleRouter

from dataskop.campaigns.api.views import CampaignViewSet, DonationUnauthorizedViewSet
from dataskop.users.api.views import UserViewSet

if settings.DEBUG:
    router = DefaultRouter()
else:
    router = SimpleRouter()

# router.register("users", UserViewSet)
router.register("donate", DonationUnauthorizedViewSet, "donate")
router.register("campaigns", CampaignViewSet, "campaigns")


app_name = "api"
urlpatterns = router.urls
