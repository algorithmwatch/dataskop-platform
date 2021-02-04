from anymail.signals import inbound
from django.conf import settings
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

from .models import Case, ReceivedMessage, Status
from .tasks import (
    persist_inbound_email,
    send_admin_notification_email,
    send_initial_emails,
)


def send_admin_waiting_approval_case():
    send_admin_notification_email(
        "Neuer Fall benötigt eine Freigabe",
        settings.URL_ORIGIN + "/admin/casehandling/case/?approval=needs_approval",
    )


@receiver(post_save, sender=Case)
def initial_email_logged_in(sender, instance: Case, created, **kwargs):
    # only sent email if the the case was just create & the user is verified
    if created:
        if instance.status == Status.WAITING_INITIAL_EMAIL_SENT:
            send_initial_emails(instance)
        elif instance.case_type.needs_approval:
            send_admin_waiting_approval_case()


# TODO: also send pending emails when the user confirmed email address with django all auth
# allauth.account.signals.email_confirmed(request, email_address)


@receiver(inbound)  # add weak=False if inside some other function/class
def handle_inbond_email(sender, event, esp_name, **kwargs):
    persist_inbound_email(event.message)
