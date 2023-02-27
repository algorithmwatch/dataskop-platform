from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from django.views.generic import View
from django_ratelimit.decorators import ratelimit

from dataskop.mailjetsync.models import NewsletterSubscription

REDIRECT_URL = "https://algorithmwatch.org/de/newsletter/vielen-dank/"


@method_decorator(ratelimit(key="ip", rate="100/h", method="GET"), name="get")
@method_decorator(never_cache, name="dispatch")
class MailjetSyncConfirmationLink(View):
    def get(self, request):
        email_str = request.GET.get("email")

        if email_str is None:
            raise PermissionDenied("Etwas stimmt nicht mit der E-Mail-Adresse.")

        obj = NewsletterSubscription.objects.filter(email=email_str).first()

        if obj is None or obj.token != request.GET.get("sesame"):
            raise PermissionDenied(
                "Der Link hat nicht funktioniert. Bitte trage dich auf unserer "
                "Webseite algorithmwatch.org in den Newsletter ein."
            )

        if obj.confirmed:
            raise PermissionDenied("Diese E-Mail-Adresse wurde bereits bestätigt.")
        else:
            ip_address = self.request.META.get("REMOTE_ADDR")
            obj.confirm(ip_address)

        return redirect(REDIRECT_URL)
