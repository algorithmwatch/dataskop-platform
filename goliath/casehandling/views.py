import json

from allauth.account.models import EmailAddress
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import IntegrityError, transaction
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.views.generic import DetailView, ListView, View
from django.views.generic.base import TemplateView
from django.views.generic.edit import UpdateView
from django.views.generic.list import ListView

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
        # if the user selected entities, we may need need to send the email to more than 1 entity
        if "awentitycheckbox" in answers:
            entity_ids = answers["awentitycheckbox"]
            case.selected_entities.add(*case_type.entities.filter(pk__in=entity_ids))
        else:
            case.selected_entities.add(case_type.entities.first())
            assert case_type.entities.all().count() == 1

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
        import json

        return render(
            request,
            "casehandling/case_new.html",
            {
                "case_type": case_type,
                "entities_values": json.dumps(
                    list(case_type.entities.values_list("id", "name"))
                ),
            },
        )


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


class CaseList(LoginRequiredMixin, ListView):
    model = Case
    template_name = "casehandling/case_list.html"

    def get_queryset(self):
        """
        limit to user
        """
        qs = Case.objects.filter(user=self.request.user)
        return qs


class HomePageView(TemplateView):
    template_name = "pages/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["featured_case_types"] = CaseType.objects.filter(
            order__isnull=False
        ).order_by("order")
        return context
