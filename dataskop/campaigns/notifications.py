from django.conf import settings
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

    def __init__(self, user):  # optionally customize the initialization
        self.context = {
            "CONTACT_EMAIL": settings.CONTACT_EMAIL,
            "user": user,
            "login_url": settings.URL_ORIGIN
            + reverse("magic_login")
            + "?email="
            + user.email,
        }  # set context for the template rendering
        self.to_emails = [user.email]  # set list of emails to send to

    @staticmethod
    def get_demo_args():  # define a static method to return list of args needed to initialize class for testing
        from django.contrib.auth import get_user_model

        User = get_user_model()

        return [User.objects.order_by("?")[0]]


@registry.register_decorator()
class ReminderEmail(UnauthorizedDonationShouldLoginEmail):
    subject = "Bitte YouTube-Datenspende bestätigen"
    template_name = "donation_reminder"


@registry.register_decorator()
class ConfirmedRegistrationEmail(EmailNotification):
    template_name = "confirmed_registration"
    subject = "DataSkop-Anmeldung erfolgreich"
    render_types = ["text"]

    def __init__(self, user):  # optionally customize the initialization
        self.context = {
            "user": user,
            "CONTACT_EMAIL": settings.CONTACT_EMAIL,
        }
        self.to_emails = [user.email]  # set list of emails to send to

    @staticmethod
    def get_demo_args():  # define a static method to return list of args needed to initialize class for testing
        from django.contrib.auth import get_user_model

        User = get_user_model()

        return [User.objects.order_by("?")[0]]


@registry.register_decorator()
class DonorNotificationEmail(EmailNotification):
    template_name = "donor_notification"
    render_types = ["text"]

    def __init__(self, user, subject, text, campaign_pk):
        magic_params = get_query_string(
            user,
            scope=f"disable-notification-{campaign_pk}",
        )
        disable_url = f"{settings.URL_ORIGIN}{reverse('donor_notification_disable')}{magic_params}&c={campaign_pk}"
        self.context = {
            "user": user,
            "CONTACT_EMAIL": settings.CONTACT_EMAIL,
            "notification_text": text,
            "disable_url": disable_url,
        }
        self.subject = subject
        self.to_emails = [user.email]

    @staticmethod
    def get_demo_args():  # define a static method to return list of args needed to initialize class for testing
        from django.contrib.auth import get_user_model

        User = get_user_model()

        return [
            User.objects.order_by("?")[0],
            "Neugikeit für Test",
            "wir haben Neugikeiten für dich.",
        ]
