import json

from django.http.response import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_control, never_cache
from django.views.generic.base import TemplateView, View
from ratelimit.decorators import ratelimit

from goliath.survey.models import Survey, SurveyAnswer

# Create your views here.


@method_decorator(
    ratelimit(
        key="user_or_ip",
        rate="casehandling.ratelimits.per_user",
        method="POST",
        block=True,
    ),
    name="post",
)
class SurveyAnswerCreateView(View):
    @method_decorator(never_cache)
    def post(self, request, pk, slug):
        survey = get_object_or_404(Survey, pk=pk)
        answers = json.loads(request.POST["answers"])

        user = None
        if request.user.is_authenticated:
            user = request.user

        SurveyAnswer.objects.create(answers=answers, user=user, survey=survey)

        # just use last case for success page for now
        return JsonResponse(
            {
                "url": reverse(
                    "survey-success",
                )
            }
        )

    @method_decorator(cache_control(max_age=3600, public=True))
    def get(self, request, pk, slug):
        survey = get_object_or_404(Survey, pk=pk)

        return render(
            request,
            "survey/answer_new.html",
            {
                "survey": survey,
            },
        )


@method_decorator(cache_control(max_age=3600, public=True), name="dispatch")
class SurveySuccess(TemplateView):
    template_name = "survey/answer_success.html"
