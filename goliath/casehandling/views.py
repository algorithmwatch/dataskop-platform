import json

from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.postgres import fields
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.utils.html import format_html
from django.views.generic import DetailView, ListView, View
from django_filters import FilterSet
from django_filters.views import FilterView
from django_tables2 import SingleTableMixin, Table

from goliath.utils.strings import random_string

from .models import Case, CaseType

User = get_user_model()


class CaseTypeList(ListView):
    model = CaseType


case_type_list_view = CaseTypeList.as_view()


class CaseCreate(LoginRequiredMixin, View):
    def post(self, request, case_type):
        case_type = get_object_or_404(CaseType, pk=case_type)
        answers = json.loads(request.POST["answers"])
        text = request.POST["text"]

        new_email = random_string(4) + "@aw.jfilter.de"
        case = Case.objects.create(
            case_type=case_type,
            email=new_email,
            text=text,
            user=self.request.user,
            entity=case_type.entity,
            answers=answers,
        )
        return JsonResponse({"url": case.get_absolute_url()})

    def get(self, request, case_type):
        case_type = get_object_or_404(CaseType, pk=case_type)
        return render(request, "casehandling/case_new.html", {"case_type": case_type})


case_create_view = CaseCreate.as_view()


class CaseDetailView(LoginRequiredMixin, DetailView):
    model = Case


case_detail_view = CaseDetailView.as_view()


class CaseFilter(FilterSet):
    class Meta:
        model = Case
        fields = ["case_type", "status", "entity"]


class CaseTable(Table):
    class Meta:
        model = Case
        template_name = "django_tables2/bootstrap.html"
        exclude = ("questions", "answers", "email")

    def render_id(self, value):
        return format_html('<a href="/anliegen/{}/">{}</a>', value, value)


class CaseList(SingleTableMixin, FilterView):
    model = Case
    table_class = CaseTable
    template_name = "casehandling/case_list.html"

    filterset_class = CaseFilter


case_list_view = CaseList.as_view()
