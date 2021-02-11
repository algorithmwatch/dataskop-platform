from django.urls import include, path, re_path
from rest_framework import routers

from .api_views import ExternalSupportViewSet
from .views import (
    CaseCreate,
    CaseDetailAndUpdate,
    CaseList,
    CaseTypeList,
    DashboardPageView,
    HomePageView,
)

router = routers.DefaultRouter()
router.register(r"externalsupport", ExternalSupportViewSet, basename="externalsupport")

urlpatterns = [
    path("", HomePageView.as_view(), name="home"),
    path("dashboard/", DashboardPageView.as_view(), name="dashboard"),
    path("api/", include(router.urls)),
    path("neu/", view=CaseTypeList.as_view(), name="new"),
    path("neu/<int:case_type>/", view=CaseCreate.as_view(), name="new-wizzard"),
    path("anliegen/", view=CaseList.as_view(), name="cases"),
    path("anliegen/<int:pk>/", view=CaseDetailAndUpdate.as_view(), name="cases-detail"),
    re_path(r"^anymail/", include("anymail.urls")),
]
