import string

from allauth.account.models import EmailAddress
from django.conf import settings
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import AbstractUser, UserManager
from django.db.models import CharField
from django.urls import reverse
from django.utils.translation import gettext_lazy as _


class CustomUserManager(UserManager):
    def create_user(self, email, first_name, last_name):
        """
        Create a user account without password.
        """
        if not email:
            raise ValueError("The given email must be set")
        email = self.normalize_email(email)

        user = self.model(email=email, first_name=first_name, last_name=last_name)
        user.set_unusable_password()
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password):
        """
        Create superuser account with email + password.
        """
        if not email:
            raise ValueError("The given email must be set")
        email = self.normalize_email(email)
        user = self.model(email=email)
        user.password = make_password(password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user

    def create_unverified_user_send_mail(self, email):
        user = self.create_user(
            first_name="first_name", last_name="last_name", email=email
        )
        # cleaned version
        email = user.email

        EmailAddress.objects.create(
            user=user, email=email, primary=True, verified=False
        )

        from ..utils.email import send_magic_link

        send_magic_link(user, email, "magic_registration")


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


User._meta.get_field("email")._unique = True
