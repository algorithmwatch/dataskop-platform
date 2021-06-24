from herald import registry
from herald.base import EmailNotification, NotificationBase

from ..utils import heraldpatches

NotificationBase.resend = classmethod(heraldpatches.resend)
EmailNotification._send = staticmethod(heraldpatches._send)


@registry.register_decorator()
class UnauthorizedDonationShouldLoginEmail(EmailNotification):
    template_name = "unauthorized_email_should_login"
    subject = "Neue Datenspenden – Bitte einloggen"

    def __init__(self, user):  # optionally customize the initialization
        self.context = {"user": user}  # set context for the template rendering
        self.to_emails = [user.email]  # set list of emails to send to

    @staticmethod
    def get_demo_args():  # define a static method to return list of args needed to initialize class for testing
        from django.contrib.auth import get_user_model

        User = get_user_model()

        return [User.objects.order_by("?")[0]]
