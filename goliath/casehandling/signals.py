from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Case

from .tasks import send_email


@receiver(post_save, sender=Case)
def initial_email(sender, instance, created, **kwargs):
    if created:
        send_email(instance, "New Case", "Hey, we have a new case for you. ;)")
