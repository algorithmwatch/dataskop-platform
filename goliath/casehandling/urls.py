from django.urls import path

from .views import case_type_list_view, case_create_view, case_detail_view

urlpatterns = [
    path("new/", view=case_type_list_view),
    path("new/<int:case_type>/", view=case_create_view),
    path("case/<int:pk>/", view=case_detail_view)
]
