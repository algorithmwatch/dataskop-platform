from rest_framework.mixins import CreateModelMixin
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet, ReadOnlyModelViewSet

from dataskop.campaigns.models import Campaign
from dataskop.campaigns.tasks import handle_donation

from .serializers import CampaignSerializer, DonationUnauthorizedSerializer


class DonationUnauthorizedViewSet(CreateModelMixin, GenericViewSet):
    """
    Only allow posting the donation.
    """

    def create(self, request, *args, **kwargs):
        """ offload to celery"""
        handle_donation.delay(request.POST)
        return Response(status=202)


class CampaignViewSet(ReadOnlyModelViewSet):
    """
    A simple ViewSet for viewing public campaigns.
    """

    queryset = Campaign.objects.filter(status="active")
    serializer_class = CampaignSerializer
