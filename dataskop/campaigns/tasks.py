import logging

from celery import shared_task
from rest_framework.parsers import JSONParser

from dataskop.campaigns.api.serializers import DonationUnauthorizedSerializer

# Get an instance of a logger
logger = logging.getLogger(__name__)


@shared_task
def handle_donation(request_data):
    serializer = DonationUnauthorizedSerializer(data=request_data)
    if serializer.is_valid():
        serializer.save()
    else:
        logger.info(
            "serialzer for unauth donation failed with the following errors:",
            serializer.errors,
        )
