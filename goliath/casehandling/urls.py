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
    admin_preview_letter_view,
    preview_letter_text,
)

router = routers.DefaultRouter()
router.register(r"externalsupport", ExternalSupportViewSet, basename="externalsupport")

urlpatterns = [
    path("", HomePageView.as_view(), name="home"),
    path("dashboard/", DashboardPageView.as_view(), name="dashboard"),
    path("neu/", view=CaseTypeList.as_view(), name="new"),
    path("neu/<str:slug>/<int:pk>/", view=CaseCreate.as_view(), name="new-wizzard"),
    path("anliegen/", view=CaseList.as_view(), name="cases"),
    path(
        "anliegen/<str:slug>/<int:pk>/",
        view=CaseDetailAndUpdate.as_view(),
        name="cases-detail",
    ),
    path(
        "falltyp-text/<int:pk>/", view=preview_letter_text, name="casetype-letter-text"
    ),
    path(
        "vorschau/<int:pk>/",
        view=admin_preview_letter_view,
        name="casetype-letter-text-admin-preview",
    ),
    re_path(r"^anymail/", include("anymail.urls")),
    re_path(r"^comments/", include("django_comments.urls")),
    path("api/", include(router.urls)),
]
