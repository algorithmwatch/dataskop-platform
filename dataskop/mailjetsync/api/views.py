from rest_framework.mixins import CreateModelMixin
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from dataskop.mailjetsync.api.serializers import NewsletterSubscriptionSerializer
from dataskop.mailjetsync.tasks import handle_newsletter_subscription


class NewsletterSubcriptionViewSet(CreateModelMixin, GenericViewSet):
    """ """

    # deserialization happens in the celery task
    serializer_class = NewsletterSubscriptionSerializer
    throttle_scope = "post_large"

    def create(self, request, *args, **kwargs):
        """
        offload to celery
        """
        ip_address = self.request.META.get("REMOTE_ADDR")

        handle_newsletter_subscription.delay(request.data, ip_address)
        return Response(status=202)
