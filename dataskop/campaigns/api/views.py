from anonip import Anonip
from rest_framework.mixins import CreateModelMixin
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet, ReadOnlyModelViewSet

from dataskop.campaigns.models import Campaign
from dataskop.campaigns.tasks import handle_donation, handle_event

from .serializers import (
    CampaignSerializer,
    DonationUnauthorizedSerializer,
    EventSerializer,
)


class DonationUnauthorizedViewSet(CreateModelMixin, GenericViewSet):
    """
    Endpoint to accept new donations (POST-only).
    """

    # deserialization happens in the celery task
    serializer_class = DonationUnauthorizedSerializer
    throttle_scope = "post_large"

    def create(self, request, *args, **kwargs):
        """
        offload to celery
        """
        ip_address = self.request.META.get("REMOTE_ADDR")

        handle_donation.delay(request.data, ip_address)
        return Response(status=202)


class EventViewSet(CreateModelMixin, GenericViewSet):
    """
    Endpoint to accept new events (POST-only).
    """

    # deserialization happens in the celery task
    serializer_class = EventSerializer
    throttle_scope = "post_small"

    def create(self, request, *args, **kwargs):
        """
        offload to celery
        """
        ip_address = self.request.META.get("REMOTE_ADDR")
        anonip = Anonip()
        # mask last digits
        ip_address = anonip.process_line(ip_address)

        handle_event.delay(request.data, ip_address)
        return Response(status=202)


class CampaignViewSet(ReadOnlyModelViewSet):
    """
    Read-only endpoint for active campaigns.
    """

    queryset = Campaign.objects.filter(status="active")
    serializer_class = CampaignSerializer
    filterset_fields = ["provider__client", "provider__name"]
