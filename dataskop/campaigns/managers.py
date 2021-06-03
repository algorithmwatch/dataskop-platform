from allauth.account.models import EmailAddress
from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class DonationManagers(models.Manager):
    def unconfirmed_donations_by_user(self, user, verified_user=True):
        assert User.objects.filter(pk=user.pk).exists()

        user_emails = EmailAddress.objects.filter(
            user=user, verified=verified_user
        ).values_list("email")
        qs = self.filter(unauthorized_email__in=user_emails, donor__isnull=True)
        return qs
