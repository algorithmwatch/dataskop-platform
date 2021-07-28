from django.dispatch import receiver

from dataskop.campaigns.notifications import ConfirmedRegistrationEmail
from dataskop.users.signals import post_magic_email_verified, pre_user_deleted

from .models import Donation, Event


@receiver(post_magic_email_verified)
def handle_verified(sender, user, email, **kwargs):
    # mark the first dontion as part of the user
    try:
        last_donation = Donation.objects.filter(
            donor__isnull=True, unauthorized_email=email
        ).earliest("created")
        last_donation.donor = user
        last_donation.ip_address = None
        last_donation.save()

        ConfirmedRegistrationEmail(user).send(user=user)

    except Donation.DoesNotExist:
        pass


@receiver(pre_user_deleted)
def handle_pre_user_deleted(sender, user, **kwargs):
    Event.objects.create(message=f"user deleted: {user.pk}")
