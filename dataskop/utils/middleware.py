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
        add_event.delay(
            message="Django exception",
            data={
                "path": request.get_full_path_info(),
                "method": request.method,
                "body": request.POST,
                "ip_address": request.META.get("REMOTE_ADDR"),
                "exception": str(exception),
            },
        )
        return None
