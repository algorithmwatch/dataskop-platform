from allauth.account.models import EmailAddress
from django.db import models


class DonationManagers(models.Manager):
    def unconfirmed_donations_by_user(self, user):
        user_emails = EmailAddress.objects.filter(user=user, verified=True).values_list(
            "email"
        )
        qs = self.filter(unauthorized_email__in=user_emails, donor__isnull=True)
        return qs
