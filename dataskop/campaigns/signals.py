"""
Listen to events (signals) generated by other apps.
"""

from django.dispatch import receiver

from dataskop.users.signals import post_magic_login, pre_user_deleted

from .models import Donation, Event


@receiver(post_magic_login)
def handle_verified(sender, user, email, ip_address, **kwargs):
    try:
        # mark the last dontion as part of the user
        last_donation = Donation.objects.filter(
            donor__isnull=True, unauthorized_email=email
        ).earliest("created")
        last_donation.confirm(user, send_email=True, ip_address=ip_address)
    except Donation.DoesNotExist:
        pass


@receiver(pre_user_deleted)
def handle_pre_user_deleted(sender, user, **kwargs):
    # store IDs for donations (that are about to get deleted)
    donations = list(Donation.objects.filter(donor=user).values("id", "campaign"))
    Event.objects.create(
        message=f"user deleted", data={"user": user.pk, "donations": donations}
    )
