from anymail.signals import inbound
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Case, MessageReceived
from .tasks import persist_inbound_email, send_initial_email


@receiver(post_save, sender=Case)
def initial_email(sender, instance, created, **kwargs):
    # only sent email if the the case was just create & the user is verified
    if created and instance.status == instance.status.WAITING_INITIAL_EMAIL_SENT:
        send_initial_email(instance, "New Case", instance.answers_text)


@receiver(inbound)  # add weak=False if inside some other function/class
def handle_inbond_email(sender, event, esp_name, **kwargs):
    persist_inbound_email(event.message)
