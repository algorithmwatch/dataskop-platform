from rest_framework.mixins import CreateModelMixin
from rest_framework.viewsets import GenericViewSet

from .serializers import DonationUnauthorized


class DonationUnauthorizedViewSet(CreateModelMixin, GenericViewSet):
    """
    Only allow posting the donation.
    """

    serializer_class = DonationUnauthorized
