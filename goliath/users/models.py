from django.contrib.auth.models import AbstractUser
from django.db.models import CharField
from django.urls import reverse
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    """Default user for Goliath."""

    first_name = CharField(_("First Name"), max_length=255)
    last_name = CharField("Last Name", max_length=255)
