from django.urls import path
from django.urls import include, re_path

from .views import (
    case_type_list_view,
    case_create_view,
    case_detail_and_update,
    case_list_view,
)

urlpatterns = [
    path("neu/", view=case_type_list_view, name="new"),
    path("neu/<int:case_type>/", view=case_create_view, name="new-wizzard"),
    path("anliegen/", view=case_list_view, name="cases"),
    path("anliegen/<int:pk>/", view=case_detail_and_update, name="cases-detail"),
    re_path(r"^anymail/", include("anymail.urls")),
]
