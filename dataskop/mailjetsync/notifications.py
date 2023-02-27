"""
The confirmation email that includes a link for the user to confirm the newsletter
subscription.

We stick to the formal language since the email text is taken from offical AW
newsletter.
"""

from django.urls.base import reverse
from django.utils.http import urlquote
from herald import registry
from herald.base import EmailNotification, NotificationBase

from ..utils import heraldpatches

NotificationBase.resend = classmethod(heraldpatches.resend)
EmailNotification._send = staticmethod(heraldpatches._send)


@registry.register_decorator()
class MailjetsyncSubscribe(EmailNotification):
    template_name = "mailjetsync_subscribe"
    subject = "Bitte bestätigen Sie Ihr Abonnement"
    render_types = ["text"]

    def __init__(self, token, email, site):
        self.to_emails = [email]
        self.from_email = site.siteextended.formatted_from

        magic_link = site.siteextended.url_origin + (
            reverse("mailjet_magic_confirm")
            + "?sesame="
            + token
            + "&email="
            + urlquote(email)
        )

        self.context = {
            "activate_url": magic_link,
        }

    @staticmethod
    def get_demo_args():
        from django.contrib.sites.models import Site

        from dataskop.users.models import User

        return [
            User.objects.order_by("?")[0],
            "peter@lustig.de",
            "127.0.0.1",
            Site.objects.first(),
        ]
