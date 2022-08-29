from django.urls.base import reverse
from django.utils.http import urlquote
from herald import registry
from herald.base import EmailNotification, NotificationBase

from ..utils import heraldpatches

NotificationBase.resend = classmethod(heraldpatches.resend)
EmailNotification._send = staticmethod(heraldpatches._send)


@registry.register_decorator()
class MagicRegistrationEmail(EmailNotification):
    template_name = "magic_registration"
    subject = "DataSkop-Anmeldung abschließen"
    render_types = ["text"]

    def __init__(
        self,
        user,
        email,
        ip_address,
        site,
    ):
        self.to_emails = [email]
        self.from_email = site.siteextended.formatted_from

        # Important to import it here because it must not get imported before the
        # declaration of our custom user model.
        from sesame.utils import get_query_string

        magic_link = site.siteextended.url_origin + (
            reverse("magic_confirm")
            + get_query_string(user, scope=email + ip_address)
            + "&email="
            + urlquote(email)
        )

        self.context = {
            "activate_url": magic_link,
            "support_email": site.siteextended.support_email,
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


@registry.register_decorator()
class MagicLoginEmail(MagicRegistrationEmail):
    template_name = "magic_login"
    subject = "DataSkop-Anmeldung"
