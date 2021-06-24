from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.core.mail import send_mail
from django.db.models import CharField
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.http import urlquote
from django.utils.translation import gettext_lazy as _

from dataskop.users.notifications import MagicLoginEmail, MagicRegistrationEmail
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

    def send_magic_registration(self, email, ip_address):
        """"""

        MagicRegistrationEmail(self, email, ip_address).send(user=self)

    def send_magic_login(self, email, ip_address):
        """"""

        MagicLoginEmail(self, email, ip_address).send(user=self)

    def send_email(self, subject, body):
        send_anymail_email(
            self.email, body, subject=subject, full_user_name=self.full_name
        )


User._meta.get_field("email")._unique = True
