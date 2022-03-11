from django.urls.base import reverse
from herald import registry
from herald.base import EmailNotification, NotificationBase
from sesame.utils import get_query_string

from ..utils import heraldpatches

NotificationBase.resend = classmethod(heraldpatches.resend)
EmailNotification._send = staticmethod(heraldpatches._send)


@registry.register_decorator()
class UnauthorizedDonationShouldLoginEmail(EmailNotification):
    template_name = "unauthorized_email_should_login"
    subject = "Neue Datenspenden – Bitte einloggen"
    render_types = ["text"]

    def __init__(self, user, site):
        self.context = {
            "support_email": site.siteextended.support_email,
            "user": user,
            "login_url": site.siteextended.url_origin
            + reverse("magic_login")
            + "?email="
            + user.email,
        }
        self.to_emails = [user.email]
        self.from_email = site.siteextended.formatted_from

    @staticmethod
    def get_demo_args():
        from django.contrib.auth import get_user_model
        from django.contrib.sites.models import Site

        User = get_user_model()

        return [
            User.objects.order_by("?")[0],
            Site.objects.first(),
        ]


@registry.register_decorator()
class ReminderEmail(UnauthorizedDonationShouldLoginEmail):
    subject = "Bitte YouTube-Datenspende bestätigen"
    template_name = "donation_reminder"


@registry.register_decorator()
class ConfirmedRegistrationEmail(EmailNotification):
    template_name = "confirmed_registration"
    subject = "DataSkop-Anmeldung erfolgreich"
    render_types = ["text"]

    def __init__(self, user, site):
        self.context = {
            "user": user,
            "support_email": site.siteextended.support_email,
        }
        self.to_emails = [user.email]
        self.from_email = site.siteextended.formatted_from

    @staticmethod
    def get_demo_args():
        from django.contrib.auth import get_user_model
        from django.contrib.sites.models import Site

        User = get_user_model()

        return [User.objects.order_by("?")[0], Site.objects.first()]


@registry.register_decorator()
class DonorNotificationEmail(EmailNotification):
    template_name = "donor_notification"
    render_types = ["text"]

    def __init__(self, user, subject, text, campaign_pk):
        from dataskop.campaigns.models import Campaign

        site = Campaign.objects.get(pk=campaign_pk).site

        magic_params = get_query_string(
            user,
            scope=f"disable-notification-{campaign_pk}",
        )
        disable_url = f"{site.siteextended.url_origin}{reverse('donor_notification_disable')}{magic_params}&c={campaign_pk}"
        self.context = {
            "user": user,
            "support_email": site.siteextended.support_email,
            "notification_text": text,
            "disable_url": disable_url,
        }
        self.subject = subject
        self.to_emails = [user.email]
        self.from_email = site.siteextended.formatted_from

    @staticmethod
    def get_demo_args():
        from django.contrib.auth import get_user_model
        from django.contrib.sites.models import Site

        from dataskop.campaigns.models import Campaign

        User = get_user_model()

        return [
            User.objects.order_by("?")[0],
            "Neugikeit für Test",
            "wir haben Neugikeiten für dich.",
            Campaign.objects.first().pk,
        ]
