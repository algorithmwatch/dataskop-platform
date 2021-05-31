from rest_framework.mixins import CreateModelMixin
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from dataskop.campaigns.tasks import handle_donation

from .serializers import DonationUnauthorizedSerializer


class DonationUnauthorizedViewSet(CreateModelMixin, GenericViewSet):
    """
    Only allow posting the donation.
    """

    def create(self, request, *args, **kwargs):
        """ offload to celery"""
        handle_donation.delay(request)
        return Response(status=202)
