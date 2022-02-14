import logging

from celery import shared_task
from django.contrib.auth import get_user_model

from dataskop.campaigns.api.serializers import (
    DonationUnauthorizedSerializer,
    EventSerializer,
)
from dataskop.campaigns.models import Donation
from dataskop.utils.email import send_admin_notification

User = get_user_model()


# Get an instance of a logger
logger = logging.getLogger(__name__)


@shared_task(acks_late=True, reject_on_worker_lost=True)
def handle_donation(request_data, ip_address):
    """
    Process POSTed data to create a donation.

    We don't enforce atomic requests because it's unlikely that an exception gets thrown
    due to external factors. If there is an exception, there is most likely a bug. And,
    we want to make sure that the donation gets persisted to the DB. All the post-save
    handling of a donation, is not essential. In the worst case, we have to retry a task
    and a donation gets duplicated (and this can be handled manually). All bugs get
    reported via sentry.

    On `acks_late` and `reject_on_worker_lost`: We want to make sure that we don't miss
    any kind of donation. If something is wrong with the worker, the donation is still
    in the queue.
    """
    request_data["ip_address"] = ip_address
    serializer = DonationUnauthorizedSerializer(data=request_data)
    if serializer.is_valid():
        serializer.save()
    else:
        logger.info(
            f"serialzer for unauth donation failed with the following errors: {serializer.errors}"
        )


@shared_task(acks_late=True, reject_on_worker_lost=True)
def handle_event(request_data, ip_address):
    """
    Process POSTed data to create an event.
    """
    request_data["ip_address"] = ip_address
    serializer = EventSerializer(data=request_data)
    if serializer.is_valid():
        serializer.save()
    else:
        logger.info(
            f"event serialer failed with: {serializer.errors}",
        )


@shared_task
def remind_user_registration():
    """
    Send reminder emails to users who didn't verify their email address.
    """
    num_reminder_sent = Donation.objects.remind_user_registration()
    if num_reminder_sent > 0:
        text = f"{num_reminder_sent} reminders sent"
        send_admin_notification(text, text)
    return num_reminder_sent


@shared_task
def test_task_email():
    """
    Test if celery beat only runs once to prevent duplicate emails.
    """
    send_admin_notification(
        "Test task e-mail",
        "this E-Mail should only be sent once.",
    )
