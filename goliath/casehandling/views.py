import datetime
import json
import traceback

from allauth.account.models import EmailAddress
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import Count
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, render
from django.urls.base import reverse
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_control, never_cache
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.views.generic import DetailView, ListView, View
from django.views.generic.base import TemplateView
from django.views.generic.edit import UpdateView
from django.views.generic.list import ListView
from ratelimit.decorators import ratelimit

from .forms import CaseStatusForm, get_admin_form_preview
from .models import Case, CaseType, PostCaseCreation
from .tasks import send_admin_notification_waiting_approval_case

User = get_user_model()


@method_decorator(cache_control(max_age=3600, public=True), name="dispatch")
class CaseTypeListView(ListView):
    model = CaseType


@method_decorator(
    ratelimit(
        key="user_or_ip",
        rate="casehandling.ratelimits.per_user",
        method="POST",
        block=True,
    ),
    name="post",
)
class CaseCreateView(View):
    @method_decorator(never_cache)
    def post(self, request, pk, slug):
        case_type = get_object_or_404(CaseType, pk=pk)
        answers = json.loads(request.POST["answers"])
        user, is_logged_in = User.objects.get_or_create_user(request, answers)

        if (
            not is_logged_in
            or not EmailAddress.objects.filter(user=user, verified=True).exists()
        ):
            status = Case.Status.WAITING_USER_VERIFIED
        elif case_type.needs_approval:
            status = Case.Status.WAITING_CASE_APPROVED
        else:
            status = Case.Status.WAITING_INITIAL_EMAIL_SENT

        # NB: currently we choose all entities by default.
        # Initially we thought that we add

        # if the user selected entities, we may need need to send the email to more than 1 entity
        # if "awentitycheckbox" in answers:
        #     entity_ids = answers["awentitycheckbox"]
        #     case.selected_entities.add(*case_type.entities.filter(pk__in=entity_ids))
        # else:

        postCC = PostCaseCreation.objects.create(user=user, case_type=case_type)

        # create new cases for all entities
        for ent in case_type.entities.all():
            case = Case.objects.create_case_with_email(
                user,
                status=status,
                case_type=case_type,
                post_cc=postCC,
                answers=answers,
            )
            case.selected_entities.add(ent)

        if status == Case.Status.WAITING_INITIAL_EMAIL_SENT:
            postCC.send_all_initial_emails()
        elif case_type.needs_approval:
            send_admin_notification_waiting_approval_case()

        # just use last case for success page for now
        if is_logged_in:
            return JsonResponse(
                {
                    "url": reverse(
                        "post-wizzard-success",
                        kwargs={"pk": postCC.pk},
                    )
                }
            )
        else:
            return JsonResponse(
                {
                    "url": reverse(
                        "post-wizzard-email",
                    )
                }
            )

    @method_decorator(cache_control(max_age=3600, public=True))
    def get(self, request, pk, slug):
        case_type = get_object_or_404(CaseType, pk=pk)

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


class CaseStatusUpdateView(UserPassesTestMixin, LoginRequiredMixin, UpdateView):
    template_name = "casehandling/case_detail.html"
    form_class = CaseStatusForm
    model = Case

    def get_success_url(self):
        return self.object.get_absolute_url()

    def test_func(self):
        obj = self.get_object()
        return obj.user == self.request.user or self.request.user.is_staff


class CaseDetailView(UserPassesTestMixin, LoginRequiredMixin, DetailView):
    model = Case

    def test_func(self):
        obj = self.get_object()
        return obj.user == self.request.user or self.request.user.is_staff

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form"] = CaseStatusForm()
        return context


@method_decorator(never_cache, name="dispatch")
class CaseDetailAndUpdateView(View):
    def get(self, request, *args, **kwargs):
        view = CaseDetailView.as_view()
        return view(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        view = CaseStatusUpdateView.as_view()
        return view(request, *args, **kwargs)


@method_decorator(never_cache, name="dispatch")
class CaseListView(LoginRequiredMixin, ListView):
    model = Case
    template_name = "casehandling/case_list.html"

    def get_queryset(self):
        """
        limit to user
        """
        qs = Case.objects.filter(user=self.request.user)
        return qs


@method_decorator(never_cache, name="dispatch")
class CaseSuccessView(
    SuccessMessageMixin, UserPassesTestMixin, LoginRequiredMixin, UpdateView
):
    model = PostCaseCreation
    fields = ["is_contactable", "post_creation_hint"]
    template_name = "casehandling/case_success.html"
    success_message = "Vielen Dank"

    def get_success_url(self):
        return self.get_object().cases.first().get_absolute_url()

    def test_func(self):
        obj = self.get_object()
        return obj.user == self.request.user


@method_decorator(cache_control(max_age=3600, public=True), name="dispatch")
class CaseVerifyEmailView(TemplateView):
    template_name = "casehandling/case_email.html"


@method_decorator(cache_control(max_age=3600, public=True), name="dispatch")
class HomePageView(TemplateView):
    template_name = "pages/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["featured_case_types"] = CaseType.objects.filter(
            order__isnull=False
        ).order_by("order")
        return context


@method_decorator(cache_control(max_age=3600, public=True), name="dispatch")
class DashboardPageView(TemplateView):
    template_name = "pages/dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # `print_status` is a propery of the model and thus we can't use the ORM's filter functions
        now = datetime.datetime.now()
        time_open_cases = [
            now - x.created_at
            for x in Case.objects.all()
            if x.print_status != "3_closed"
        ]
        context["num_open_cases"] = len(time_open_cases)
        context["avg_time_open_cases"] = (
            sum(time_open_cases, datetime.timedelta(0, 0)).days / len(time_open_cases)
            if len(time_open_cases) > 0
            else 0
        )

        time_closed_cases = [
            now - x.created_at
            for x in Case.objects.all()
            if x.print_status == "3_closed"
        ]
        context["num_closed_cases"] = len(time_closed_cases)
        context["avg_time_closed_cases"] = (
            sum(time_closed_cases, datetime.timedelta(0, 0)).days
            / len(time_closed_cases)
            if len(time_closed_cases) > 0
            else 0
        )

        # most used case types
        context["top_case_types"] = CaseType.objects.annotate(
            total=Count("case")
        ).order_by("-total")[:3]

        return context


@never_cache
@staff_member_required
def admin_preview_letter_view(request, pk):
    ct = get_object_or_404(CaseType, pk=pk)

    AdminPreviewForm = get_admin_form_preview(ct)
    letter_text = None
    render_error_message = None

    if request.method == "POST":
        form = AdminPreviewForm(request.POST)
        if form.is_valid():
            username = (
                form.cleaned_data["username"] if "username" in form.cleaned_data else ""
            )
            try:
                letter_text = ct.render_letter(dict(form.cleaned_data), username)
            except Exception as e:
                render_error_message = str(e)

                render_error_message += "\n\n".join(
                    traceback.format_exception(
                        etype=type(e), value=e, tb=e.__traceback__
                    )
                )

    else:
        form = AdminPreviewForm()

    return render(
        request,
        "casehandling/casetype_preview_letter.html",
        {
            "form": form,
            "letter_text": letter_text,
            "case_type": ct,
            "error": render_error_message,
        },
    )


@never_cache
@require_POST
@csrf_exempt
def preview_letter_text_view(request, pk):
    ct = get_object_or_404(CaseType, pk=pk)
    answers = json.loads(request.POST["answers"])
    username = request.POST["username"] if "username" in request.POST else ""
    return HttpResponse(ct.render_letter(answers, username), content_type="text/plain")
