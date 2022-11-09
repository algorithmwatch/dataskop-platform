from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from django.views.generic import View
from ratelimit.decorators import ratelimit
from sesame.utils import get_user

from dataskop.mailjetsync.models import NewsletterSubscription

REDIRECT_URL = "https://algorithmwatch.org/de/newsletter/vielen-dank/"


@method_decorator(
    ratelimit(key="ip", rate="100/h", method="GET", block=True), name="get"
)
@method_decorator(never_cache, name="dispatch")
class MailjetSyncConfirmationLink(View):
    def get(self, request):
        email_str = request.GET.get("email")

        if email_str is None:
            raise PermissionDenied("Etwas stimmt nicht mit der E-Mail-Adresse.")

        obj = NewsletterSubscription.objects.get(
            email=email_str, confirmed_at__isnull=True
        )

        if obj is None or obj.token != request.GET.get("sesame"):
            raise PermissionDenied(
                "Der Link hat nicht funktioniert. Bitte trage dich auf unserer Webseite algorithmwatch.org in den Newsletter ein."
            )

        obj.confirm()

        return redirect(REDIRECT_URL)
