from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView
from django.views.generic.edit import CreateView

from .models import Case, CaseType

User = get_user_model()

from goliath.utils.strings import random_string


class CaseTypeList(ListView):
    model = CaseType


case_type_list_view = CaseTypeList.as_view()


class CaseCreate(LoginRequiredMixin, CreateView):
    model = Case
    fields = ["questions", "answers"]

    def form_valid(self, form):
        form.instance.user = self.request.user
        form.instance.case_type = CaseType.objects.get(pk=self.kwargs["case_type"])
        form.instance.email = self.request.user.name + random_string(4) + "@aw.jfilter.de"
        return super(CaseCreate, self).form_valid(form)


case_create_view = CaseCreate.as_view()


class CaseDetailView(LoginRequiredMixin, DetailView):
    model = Case


case_detail_view = CaseDetailView.as_view()
