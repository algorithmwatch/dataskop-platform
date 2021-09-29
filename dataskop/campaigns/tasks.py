import logging

from celery import shared_task
from django.contrib.auth import get_user_model

from dataskop.campaigns.api.serializers import (
    DonationUnauthorizedSerializer,
    EventSerializer,
)
from dataskop.campaigns.models import Donation
from dataskop.utils.email import send_admin_notifcation

User = get_user_model()


# Get an instance of a logger
logger = logging.getLogger(__name__)


@shared_task
def handle_donation(request_data, ip_address):
    request_data["ip_address"] = ip_address
    serializer = DonationUnauthorizedSerializer(data=request_data)
    if serializer.is_valid():
        serializer.save()
    else:
        logger.info(
            f"serialzer for unauth donation failed with the following errors: {serializer.errors}"
        )


@shared_task
def handle_event(request_data, ip_address):
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
    return Donation.objects.remind_user_registration()


@shared_task
def test_task_email():
    """
    A simple task to check if celery beat only runs once to prevent duplicate emails.
    """
    send_admin_notifcation(
        "Test Task E-Mail",
        "this E-Mail should only be sent once.",
    )
