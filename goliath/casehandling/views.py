import json

from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.views.generic import DetailView, ListView, View

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
        new_email = random_string(4) + "@aw.jfilter.de"
        case = Case.objects.create(
            case_type=case_type,
            email=new_email,
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
