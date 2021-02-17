from django.urls import include, path, re_path
from rest_framework import routers

from .api_views import ExternalSupportViewSet
from .views import (
    CaseCreateView,
    CaseDetailAndUpdateView,
    CaseListView,
    CaseSuccessView,
    CaseTypeListView,
    CaseVerifyEmailView,
    DashboardPageView,
    HomePageView,
    admin_preview_letter_view,
    preview_letter_text_view,
)

router = routers.DefaultRouter()
router.register(r"externalsupport", ExternalSupportViewSet, basename="externalsupport")

urlpatterns = [
    path("", HomePageView.as_view(), name="home"),
    path("dashboard/", DashboardPageView.as_view(), name="dashboard"),
    path("neu/", view=CaseTypeListView.as_view(), name="new"),
    path("neu/<str:slug>/<int:pk>/", view=CaseCreateView.as_view(), name="new-wizzard"),
    path(
        "erfolg/<str:slug>/<int:pk>/",
        view=CaseSuccessView.as_view(),
        name="post-wizzard-success",
    ),
    path(
        "email-bestaetigen/",
        view=CaseVerifyEmailView.as_view(),
        name="post-wizzard-email",
    ),
    path("anliegen/", view=CaseListView.as_view(), name="cases"),
    path(
        "anliegen/<str:slug>/<int:pk>/",
        view=CaseDetailAndUpdateView.as_view(),
        name="cases-detail",
    ),
    path(
        "falltyp-text/<int:pk>/",
        view=preview_letter_text_view,
        name="casetype-letter-text",
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
