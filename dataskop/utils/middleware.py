from dataskop.campaigns.tasks import add_event


class EventExceptionsMiddelware:
    def __init__(self, get_response):
        pass

    def process_exception(self, request, exception):
        add_event.delay(
            message="Django exception",
            data={
                "path": request.get_full_path_info(),
                "method": request.method,
                "body": request.body,
                "ip_address": request.META.get("REMOTE_ADDR"),
                "exception": str(exception),
            },
        )
        return None
