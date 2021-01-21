from django.contrib.auth.models import AbstractUser
from django.db.models import CharField
from django.urls import reverse
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    """Default user for Goliath."""

    # simplier to not remove username completly
    username = CharField(max_length=255, blank=True)
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    first_name = CharField(_("First Name"), max_length=255)
    last_name = CharField("Last Name", max_length=255)

    def get_absolute_url(self):
        return reverse("account_index")


User._meta.get_field("email")._unique = True
