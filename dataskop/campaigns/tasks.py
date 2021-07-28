import logging

from celery import shared_task
from django.contrib.auth import get_user_model
from herald.models import SentNotification

from dataskop import campaigns
from dataskop.campaigns.api.serializers import (
    DonationUnauthorizedSerializer,
    EventSerializer,
)
from dataskop.campaigns.models import Donation
from dataskop.campaigns.notifications import ReminderEmail

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
