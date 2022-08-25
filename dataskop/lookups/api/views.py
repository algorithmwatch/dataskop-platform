from rest_framework.response import Response
from rest_framework.viewsets import ViewSet
from rest_framework_api_key.permissions import HasAPIKey

from dataskop.lookups.models import Lookup
from dataskop.lookups.tasks import handle_new_lookups

from .serializers import LookupSerializer


class PublicLookupViewSet(ViewSet):
    throttle_scope = "post_large"

    def list(self, request):
        pks = request.GET.getlist("l")
        objects = (
            Lookup.objects.filter(data__isnull=False)
            .exclude(data="waiting")
            .in_bulk(pks)
        )
        serializer = LookupSerializer(objects.values(), many=True)
        return Response(serializer.data)

    def create(self, request):
        handle_new_lookups.delay(request.data)
        return Response(status=202)


class InternalLookupViewSet(ViewSet):
    """
    Internal API for the scraping workers
    """

    permission_classes = [HasAPIKey]

    def list(self, request):
        """
        Get lookups to work on
        """
        objects = Lookup.objects.filter(data__isnull=True)[:50]

        # Set a text to avoid duplicated work
        objects.update(data="waiting")

        serializer = LookupSerializer(objects, many=True)
        return Response(serializer.data)

    def update(self, request, pk=None):
        """
        Update scraping results
        """
        keys = request.data.keys()
        objects = Lookup.objects.all().in_bulk(keys)

        for k in keys:
            o = objects[k]
            o.data = request.data[o.id]

        Lookup.objects.bulk_update(objects.values(), ["data"])
        return Response(status=204)

    def create(self, request):
        """
        Add new empty lookups that need to be worked on
        """
        handle_new_lookups.delay(request.data)
        return Response(status=202)
