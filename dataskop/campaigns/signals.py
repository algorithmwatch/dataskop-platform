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
        last_donation.save()
        ConfirmedRegistrationEmail(user, last_donation.campaign.site).send(user=user)

    except Donation.DoesNotExist:
        pass


@receiver(pre_user_deleted)
def handle_pre_user_deleted(sender, user, **kwargs):
    # store IDs for donations (that are about to get deleted)
    donations = list(Donation.objects.filter(donor=user).values("id", "campaign"))
    Event.objects.create(
        message=f"user deleted", data={"user": user.pk, "donations": donations}
    )
