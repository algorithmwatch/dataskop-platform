import datetime

from rest_framework.response import Response
from rest_framework.viewsets import ViewSet
from rest_framework_api_key.permissions import HasAPIKey

from dataskop.lookups.models import Lookup, LookupJob

from .serializers import BinaryField, LookupJobSerializer, LookupSerializer


class PublicLookupViewSet(ViewSet):
    def list(self, request):
        pks = request.GET.getlist("l")
        objects = Lookup.objects.in_bulk(pks)
        serializer = LookupSerializer(objects.values(), many=True)
        return Response(serializer.data)


class LookupJobViewSet(ViewSet):
    """
    Internal API for the scraping workers
    """

    permission_classes = [HasAPIKey]

    def list(self, request):
        """
        Get lookup job to work on
        """
        qs = LookupJob.objects.filter(done=False, processing=False, error=False)

        resp_obj = None
        ready_input = qs.filter(input_done__isnull=False).first()
        if ready_input:
            resp_obj = ready_input
        else:
            resp_obj = qs.first()

        if resp_obj:
            processing_objs = LookupJob.objects.filter(
                processing=True, input_todo__isnull=False
            ).values_list("input_todo", flat=True)
            processing_objs = set(sum(processing_objs, []))

            # Mark object as `processing` asap to avoid duplicated work
            resp_obj.processing = True
            resp_obj.save(update_fields=["processing"])

            # 1) Don't scrape data that is already getting processed.
            # 2) Don't scrape data that is already there. This can happen because time
            # elapsed since the upload. But don't save the updated data!
            resp_obj.input_todo = [
                x
                for x in resp_obj.input_todo
                if x not in processing_objs and not Lookup.objects.filter(id=x).exists()
            ]

            if not resp_obj.input_todo and not resp_obj.input_done:
                # Revert marking, but don't save `input_todo` since this may delete items.
                resp_obj.processing = False
                resp_obj.save(update_fields=["processing"])
                return Response(status=204)

            ser = LookupJobSerializer(resp_obj)
            return Response(ser.data)
        else:
            # Nothing to do
            return Response(status=204)

    def update(self, request, pk=None):
        """
        Update lookups and lookup job
        """
        job = LookupJob.objects.get(pk=pk)

        bin_field = BinaryField()

        if "results" in request.data:
            new_lookups = [
                Lookup(id=k, data=bin_field.to_internal_value(v), job=job)
                for k, v in request.data["results"].items()
            ]
            # ignore lookups that are now already inserted
            Lookup.objects.bulk_create(new_lookups, ignore_conflicts=True)

        if "log" in request.data:
            job.log += (
                datetime.datetime.now().isoformat() + " " + request.data["log"] + "\n"
            )

        if "done" in request.data and request.data["done"]:
            job.processing = False
            job.done = True

        if "error" in request.data and request.data["error"]:
            job.processing = False
            job.error = True

        job.save(update_fields=["log", "done", "processing", "error"])
        return Response(status=204)

    def create(self, request):
        """
        Add a new lookup job with lookup ids
        """

        log = (
            datetime.datetime.now().isoformat()
            + " "
            + getattr(request.data, "log", "Creating a new job")
            + "\n"
        )
        LookupJob.objects.create_chunked_todo(
            input_todo=request.data["todo"], log=log, trusted=True
        )
        return Response(status=201)
