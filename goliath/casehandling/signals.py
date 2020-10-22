from anymail.signals import inbound
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Case, ReceivedMessage
from .tasks import send_initial_email, persist_inbound_email


@receiver(post_save, sender=Case)
def initial_email(sender, instance, created, **kwargs):
    if created:
        send_initial_email(instance, "New Case", "Hey, we have a new case for you. ;)")


@receiver(inbound)  # add weak=False if inside some other function/class
def handle_inbond_email(sender, event, esp_name, **kwargs):
    persist_inbound_email(event.message)
