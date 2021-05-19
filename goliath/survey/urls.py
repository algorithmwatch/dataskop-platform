from django.urls import path

from goliath.survey.views import SurveyAnswerCreateView, SurveySuccess

urlpatterns = [
    path("umfrage-erfolg", SurveySuccess.as_view(), name="survey-success"),
    path(
        "umfrage/<str:slug>/<int:pk>/",
        view=SurveyAnswerCreateView.as_view(),
        name="survey-new",
    ),
]
