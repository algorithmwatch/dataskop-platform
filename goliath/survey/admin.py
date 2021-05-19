from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin

from goliath.casehandling.admin import (
    HistoryDeletedFilter,
    HistoryDeletedFilterMixin,
    RemoveAdminAddButtonMixin,
)
from goliath.survey.models import Survey, SurveyAnswer


class SurveyAdmin(HistoryDeletedFilterMixin, SimpleHistoryAdmin):
    list_display = [
        "id",
        "created_at",
        "title",
    ]
    view_on_site = True


class SurveyAnswerAdmin(RemoveAdminAddButtonMixin, SimpleHistoryAdmin):
    list_display = [
        "id",
        "created_at",
        "survey",
        "user",
    ]

    list_filter = (HistoryDeletedFilter,)
    view_on_site = False


admin.site.register(Survey, SurveyAdmin)
admin.site.register(SurveyAnswer, SurveyAnswerAdmin)
