from django.dispatch import receiver

from dataskop.users.signals import post_magic_email_verified

from .models import Donation


@receiver(post_magic_email_verified)
def handle_verified(sender, request, user, email, **kwargs):
    last_donation = Donation.objects.filter(
        donor__isnull=True, unauthorized_email=email
    ).earliest("created")
    last_donation.donor = user
    last_donation.save()
