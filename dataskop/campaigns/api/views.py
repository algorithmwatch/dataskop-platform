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
    Only allow posting the donation.
    """

    # not needed right now, but GET requests cause 500ers without `serializer_class`
    serializer_class = DonationUnauthorizedSerializer

    def create(self, request, *args, **kwargs):
        """offload to celery"""
        ip_address = self.request.META.get("REMOTE_ADDR")

        handle_donation.delay(request.data, ip_address)
        return Response(status=202)


class EventViewSet(CreateModelMixin, GenericViewSet):
    """
    Only allow posting the donation.
    """

    # not needed right now, but GET requests cause 500ers without `serializer_class`
    serializer_class = EventSerializer

    def create(self, request, *args, **kwargs):
        """offload to celery"""
        ip_address = self.request.META.get("REMOTE_ADDR")

        anonip = Anonip()

        # mask last digits
        ip_address = anonip.process_line(ip_address)

        handle_event.delay(request.data, ip_address)
        return Response(status=202)


class CampaignViewSet(ReadOnlyModelViewSet):
    """
    A simple ViewSet for viewing public campaigns.
    """

    queryset = Campaign.objects.filter(status="active")
    serializer_class = CampaignSerializer
