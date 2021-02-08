import json

from allauth.account.models import EmailAddress
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import IntegrityError, transaction
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.utils.html import format_html
from django.views.generic import DetailView, ListView, View
from django.views.generic.edit import UpdateView
from django_filters import FilterSet
from django_filters.views import FilterView
from django_tables2 import SingleTableMixin, Table

from ..utils.email import send_magic_link
from .forms import CaseStatusForm
from .models import Case, CaseType, Status
from .tasks import send_admin_waiting_approval_case, send_initial_emails

User = get_user_model()


def get_user_for_case(request, answers):
    """
    Create a new user or return current logged in user
    """
    is_logged_in = request.user.is_authenticated
    if is_logged_in:
        user = request.user
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

        send_magic_link(user, email, "magic_registration")
    return user, is_logged_in


class CaseTypeList(ListView):
    model = CaseType


class CaseCreate(View):
    def post(self, request, case_type):
        case_type = get_object_or_404(CaseType, pk=case_type)
        answers = json.loads(request.POST["answers"])
        text = request.POST["text"]
        user, is_logged_in = get_user_for_case(request, answers)

        if (
            not is_logged_in
            or not EmailAddress.objects.filter(user=user, verified=True).exists()
        ):
            status = Status.WAITING_USER_VERIFIED
        elif case_type.needs_approval:
            status = Status.WAITING_CASE_APPROVED
        else:
            # this will send the initial email via Signal
            status = Status.WAITING_INITIAL_EMAIL_SENT

        # try 20 times to generate unique email for this case and then give up
        # increase the number of digits for each try
        error_count = 0
        while True:
            try:
                # Nest the already atomic transaction to let the database safely fail.
                with transaction.atomic():
                    case = Case.objects.create(
                        case_type=case_type,
                        email=user.gen_case_email(error_count + 1),
                        answers_text=text,
                        user=user,
                        answers=answers,
                        status=status,
                    )
                break
            except IntegrityError as e:
                if "unique constraint" in e.args[0]:
                    error_count += 1
                    if error_count > 20:
                        raise e

        # FIXME
        case.selected_entities.add(*case_type.entities.all())

        if case.status == Status.WAITING_INITIAL_EMAIL_SENT:
            send_initial_emails(case)
        elif case.case_type.needs_approval:
            send_admin_waiting_approval_case()

        # FIXME
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
    # filter by "entities"
    class Meta:
        model = Case
        fields = ["case_type", "status"]


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
