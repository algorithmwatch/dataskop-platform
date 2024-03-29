from django.contrib.auth.models import AbstractUser
from django.db.models import CharField
from django.urls import reverse
from django_lifecycle import BEFORE_DELETE, LifecycleModelMixin, hook

from dataskop.users.notifications import MagicLoginEmail, MagicRegistrationEmail

from .managers import CustomUserManager
from .signals import pre_user_deleted


class User(LifecycleModelMixin, AbstractUser):
    """Default user for dataskop."""

    # easier to override username
    username = CharField(max_length=255, blank=True, null=True)  # type: ignore
    USERNAME_FIELD: str = "email"
    REQUIRED_FIELDS: list = []

    first_name = CharField("Vorname", max_length=255)
    last_name = CharField("Nachname", max_length=255)

    objects = CustomUserManager()

    @property
    def full_name(self):
        return self.first_name + " " + self.last_name

    def get_absolute_url(self):
        return reverse("account_index")

    def send_magic_registration(self, email, ip_address, site, donation):
        return MagicRegistrationEmail(self, email, ip_address, site, donation).send(
            user=self
        )

    def send_magic_login(self, email, ip_address, site):
        return MagicLoginEmail(self, email, ip_address, site).send(user=self)

    @hook(BEFORE_DELETE)
    def before_delete_hook(self):
        pre_user_deleted.send(self, user=self)


User._meta.get_field("email")._unique = True  # type: ignore
