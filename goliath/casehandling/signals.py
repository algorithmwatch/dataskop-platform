from anymail.signals import inbound
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

from .models import Case, ReceivedMessage
from .tasks import persist_inbound_email, send_initial_emails


@receiver(post_save, sender=Case)
def initial_email_logged_in(sender, instance: Case, created, **kwargs):
    # only sent email if the the case was just create & the user is verified
    if created and instance.status == instance.status.WAITING_INITIAL_EMAIL_SENT:
        send_initial_emails(instance, "New Case", instance.answers_text)


@receiver(pre_save, sender=Case)
def initial_email_verified(sender, instance: Case, **kwargs):
    # check if model is was already created
    if instance.id is not None:
        previous = Case.objects.get(id=instance.id)
        # check if status is about to update
        if previous.status != instance.status:
            if instance.status == instance.status.WAITING_INITIAL_EMAIL_SENT:
                send_initial_emails(instance, "New Case", instance.answers_text)


@receiver(inbound)  # add weak=False if inside some other function/class
def handle_inbond_email(sender, event, esp_name, **kwargs):
    persist_inbound_email(event.message)
