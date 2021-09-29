from django.contrib.auth.models import AbstractUser
from django.db.models import CharField
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from dataskop.users.notifications import MagicLoginEmail, MagicRegistrationEmail

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
        return MagicRegistrationEmail(self, email, ip_address).send(user=self)

    def send_magic_login(self, email, ip_address):
        return MagicLoginEmail(self, email, ip_address).send(user=self)



User._meta.get_field("email")._unique = True
