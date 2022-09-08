from dataskop.campaigns.tasks import add_event


class EventExceptionsMiddelware:
    def __init__(self, get_response):
        self.get_response = get_response
        # One-time configuration and initialization.

    def __call__(self, request):
        # Code to be executed for each request before
        # the view (and later middleware) are called.

        response = self.get_response(request)

        # Code to be executed for each request/response after
        # the view is called.

        return response

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
