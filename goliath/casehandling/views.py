import json

from allauth.account.models import EmailAddress
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.utils.crypto import get_random_string
from django.utils.html import format_html
from django.views.generic import DetailView, ListView, View
from django.views.generic.edit import UpdateView
from django_filters import FilterSet
from django_filters.views import FilterView
from django_tables2 import SingleTableMixin, Table

from ..utils.magic_link import send_magic_link
from .forms import CaseStatusForm
from .models import Case, CaseType, Status

User = get_user_model()


class CaseTypeList(ListView):
    model = CaseType


class CaseCreate(View):
    def post(self, request, case_type):
        case_type = get_object_or_404(CaseType, pk=case_type)
        answers = json.loads(request.POST["answers"])
        text = request.POST["text"]

        is_logged_in = request.user.is_authenticated
        if is_logged_in:
            user = self.request.user
        else:
            # need to create a new, unverified user
            # https://stackoverflow.com/q/29147550/4028896

            first_name, last_name, email = (
                answers["awfirstnamequestion"],
                answers["awlastnamequestion"],
                answers["awemailquestion"],
            )
            user = User.objects.create_user(
                first_name=first_name, last_name=last_name, email=email
            )
            # cleaned version
            email = user.email

            EmailAddress.objects.create(
                user=user, email=email, primary=True, verified=False
            )

            send_magic_link(request, user, email, "magic_registration")

        status = (
            Status.WAITING_INITIAL_EMAIL_SENT
            if is_logged_in
            else Status.WAITING_USER_VERIFIED
        )

        new_email = get_random_string(4).lower() + "@" + settings.DEFAULT_EMAIL_DOMAIN

        case = Case.objects.create(
            case_type=case_type,
            email=new_email,
            answers_text=text,
            user=user,
            entity=case_type.entity,
            answers=answers,
            status=status,
        )

        # is this enough?
        if is_logged_in:
            return JsonResponse({"url": case.get_absolute_url()})
        else:
            return JsonResponse({"url": case.get_absolute_url()})

    def get(self, request, case_type):
        case_type = get_object_or_404(CaseType, pk=case_type)
        return render(request, "casehandling/case_new.html", {"case_type": case_type})


class CaseStatusUpdateView(LoginRequiredMixin, UpdateView):
    """
    Adapted from https://docs.djangoproject.com/en/3.1/topics/class-based-views/mixins/
    """

    template_name = "casehandling/case_detail.html"
    form_class = CaseStatusForm
    model = Case

    def get_success_url(self):
        return self.object.get_absolute_url()


class CaseDetailView(LoginRequiredMixin, DetailView):
    model = Case

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form"] = CaseStatusForm()
        return context


class CaseDetailAndUpdate(View):
    def get(self, request, *args, **kwargs):
        view = CaseDetailView.as_view()
        return view(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        view = CaseStatusUpdateView.as_view()
        return view(request, *args, **kwargs)


class CaseFilter(FilterSet):
    class Meta:
        model = Case
        fields = ["case_type", "status", "entity"]


class CaseTable(Table):
    # TODO: proper templates
    class Meta:
        model = Case
        template_name = "django_tables2/bootstrap.html"
        exclude = ("questions", "answers", "email", "answers_text", "user")

    def render_id(self, value):
        return format_html('<a href="/anliegen/{}/">{}</a>', value, value)


class CaseList(LoginRequiredMixin, SingleTableMixin, FilterView):
    model = Case
    table_class = CaseTable
    template_name = "casehandling/case_list.html"

    filterset_class = CaseFilter

    def get_queryset(self):
        """
        limit to user
        """
        qs = Case.objects.filter(user=self.request.user)
        return qs
