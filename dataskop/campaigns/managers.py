from allauth.account.models import EmailAddress
from django.contrib.auth import get_user_model
from django.db import models
from herald.models import SentNotification

from dataskop.campaigns.notifications import ReminderEmail

User = get_user_model()


class DonationManagers(models.Manager):
    def unconfirmed_donations_by_user(self, user, verified_user=True):
        assert User.objects.filter(pk=user.pk).exists()

        user_emails = EmailAddress.objects.filter(
            user=user, verified=verified_user
        ).values_list("email")
        qs = self.filter(unauthorized_email__in=user_emails, donor__isnull=True)
        return qs

    def remind_user_registration(self, donation_qs=None):
        total_reminder_sent = 0

        # only remind for:
        # - unverfied donations (donor is null)
        # - active campaigns
        qs = (donation_qs or self.model.objects).filter(
            donor__isnull=True,
            unauthorized_email__isnull=False,
            campaign__isnull=False,
            campaign__status="active",
        )

        for email in qs.values_list("unauthorized_email", flat=True).distinct():
            user = User.objects.filter(email=email).first()
            if user is None:
                continue

            # If users donate more than 1 time, it can happen that there unconfirmed donations.
            # User's have to manually mark them as their donations but we don't need to remind for registration.
            if EmailAddress.objects.filter(user=user, verified=True).exists():
                continue

            num_sent = SentNotification.objects.filter(
                user=user,
                notification_class="dataskop.campaigns.notifications.ReminderEmail",
            ).count()

            if num_sent < 5:
                ReminderEmail(user).send(user=user)

                total_reminder_sent += 1
        return total_reminder_sent
