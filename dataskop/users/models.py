from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.core.mail import send_mail
from django.db.models import CharField
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.http import urlquote
from django.utils.translation import gettext_lazy as _

from dataskop.utils.email import formated_from, send_anymail_email

from .managers import CustomUserManager


class User(AbstractUser):
    """Default user for dataskop."""

    # easier to override username
    username = CharField(max_length=255, blank=True, null=True)
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    first_name = CharField("Vorname", max_length=255)
    last_name = CharField("Nachname", max_length=255)

    objects = CustomUserManager()

    @property
    def full_name(self):
        return self.first_name + " " + self.last_name

    def get_absolute_url(self):
        return reverse("account_index")

    def send_magic_link(self, email, ip_address, viewname):
        """
        Sending the email via django's send_mail because we do need the special features of anymail.
        """

        # important to import it here because it must not get imported before the declaration of our custom user model.
        from sesame.utils import get_query_string

        magic_link = settings.URL_ORIGIN + (
            reverse(viewname)
            + get_query_string(self, scope=email + ip_address)
            + "&email="
            + urlquote(email)
        )

        context = {"activate_url": magic_link}

        subject = render_to_string("account/email/email_confirmation_subject.txt")
        body_text = render_to_string(
            "account/email/email_confirmation_message.txt",
            context,
        )
        body_html = render_to_string(
            "account/email/email_confirmation_message.html",
            context,
        )

        send_mail(
            subject,
            body_text,
            formated_from(),
            [email],
            html_message=body_html,
        )

    def send_email(self, subject, body):
        send_anymail_email(
            self.email, body, subject=subject, full_user_name=self.full_name
        )


User._meta.get_field("email")._unique = True
