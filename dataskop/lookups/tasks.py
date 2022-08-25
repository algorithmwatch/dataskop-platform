from celery import shared_task

from dataskop.lookups.models import Lookup


@shared_task(queue="low_priority", acks_late=True, reject_on_worker_lost=True)
def handle_new_lookups(request_data):
    """
    Process POSTed data to create new lookups.
    """

    # `ignore_conflicts` ensure duplicated ids are ignored
    Lookup.objects.bulk_create(
        [Lookup(id=x) for x in request_data["lookups"]], ignore_conflicts=True
    )
