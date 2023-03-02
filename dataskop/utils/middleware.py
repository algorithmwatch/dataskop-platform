from django.http import Http404

from dataskop.campaigns.tasks import add_event


class EventExceptionsMiddelware:
    """
    Store exceptions (e.g. permission denied, rate limited) in events.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        return self.get_response(request)

    def process_exception(self, request, exception):
        if isinstance(exception, Http404):
            return None

        add_event.delay(
            message=f"Django exception: {str(type(exception))}",
            data={
                "path": request.get_full_path_info(),
                "method": request.method,
                "body": request.POST,
                "ip_address": request.META.get("REMOTE_ADDR"),
                "exception_message": str(exception),
            },
        )

        return None
