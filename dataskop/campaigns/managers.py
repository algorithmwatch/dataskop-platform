from collections import defaultdict
from datetime import datetime, timedelta
from typing import Dict

from allauth.account.models import EmailAddress
from django.contrib.auth import get_user_model
from django.db import models
from herald.models import SentNotification

User = get_user_model()


class DonationQuerySet(models.QuerySet):
    def confirmed(self):
        """
        Get confirmed donations.
        """
        return self.filter(donor__isnull=False)

    def unconfirmed(self):
        """
        Get unconfirmed donations.
        """
        return self.filter(
            donor__isnull=True,
            unauthorized_email__isnull=False,
        )

    def unconfirmed_by_user(self, user, verified_user=True):
        """
        Get unconfirmed donations for a given user.
        """
        user_emails = EmailAddress.objects.filter(
            user=user, verified=verified_user
        ).values_list("email")
        return self.unconfirmed().filter(unauthorized_email__in=user_emails)


class BaseDonationManager(models.Manager):
    def remind_user_registration(self, donation_qs=None, max_reminders_sent=10):
        """
        Remind users that they have to confirm email their address.
        """

        from dataskop.campaigns.tasks import send_reminder_email

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
        # NB: Only works with Postgres:
        # https://docs.djangoproject.com/en/3.2/ref/models/querysets/#distinct
        for obj in (
            qs.order_by("unauthorized_email", "campaign")
            .distinct("unauthorized_email", "campaign")
            .select_related("campaign__site")
        ):
            user = User.objects.filter(email=obj.unauthorized_email).first()
            if user is None:
                continue

            # If users donate more than 1 time, it can happen that there unconfirmed
            # donations.
            # User's have to manually mark them as their donations but we don't need to
            # remind for registration.
            if EmailAddress.objects.filter(user=user, verified=True).exists():
                continue

            num_sent = SentNotification.objects.filter(
                user=user,
                notification_class="dataskop.campaigns.notifications.ReminderEmail",
            ).count()

            # give up after some tries
            if num_sent < max_reminders_sent:
                send_reminder_email.delay(user.pk, obj.campaign.site.pk)
                total_reminder_sent += 1

        return total_reminder_sent

    def delete_anonymous_donations(self, donation_qs=None):
        """
        delete donations that have no unauthorized emails
        """
        _, deleted = (
            (donation_qs or self.model.objects)
            .filter(
                donor__isnull=True,
                unauthorized_email__isnull=True,
            )
            .delete()
        )
        return sum(deleted.values())

    def delete_unconfirmed_donations(self, donation_qs=None):
        """
        Delete unconfirmed donations that are older than 24 hours.
        """

        deleted_objects = []
        # select unconfirmed donations
        qs = (donation_qs or self.model.objects).unconfirmed()

        # Only select those donations that can safely be deleted. Do not delete
        # unconfirmed donations that:
        # - are attached to an email address that is assigned to a verified user
        # - were created only recently (up to 24h ago)
        for email in qs.values_list("unauthorized_email", flat=True).distinct():
            email_obj = EmailAddress.objects.filter(email=email).first()

            if email_obj is None:
                # If no email exists, something is wrong. Delete it.
                _, deleted = self.model.objects.filter(
                    unauthorized_email=email
                ).delete()
                deleted_objects.append(deleted)

            elif email_obj.verified:
                # The donation is not marked as part of the user, but a verified account
                # exists. So don't delete it.
                continue
            else:

                # Do not delete donations / users that were created up to 24h ago.
                if email_obj.user.date_joined > datetime.now() - timedelta(hours=24):
                    continue

                # A user can have multiple email addresses. Maybe another was was already
                # verified? If yes, to nothing.
                if not EmailAddress.objects.filter(
                    user=email_obj.user, verified=True
                ).exists():
                    _, deleted = qs.filter(unauthorized_email=email).delete()
                    deleted_objects.append(deleted)

                    _, deleted = EmailAddress.objects.filter(
                        user=email_obj.user
                    ).delete()
                    deleted_objects.append(deleted)

                    _, deleted = email_obj.user.delete()
                    deleted_objects.append(deleted)

        total_deleted: Dict[str, int] = defaultdict(lambda: 0)

        for li in deleted_objects:
            for k, v in li.items():
                total_deleted[k] += v

        return total_deleted


DonationManager = BaseDonationManager.from_queryset(DonationQuerySet)
