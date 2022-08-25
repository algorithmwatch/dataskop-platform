from rest_framework.throttling import ScopedRateThrottle


class PostScopedRateThrottle(ScopedRateThrottle):
    """
    Only throttle post requests.
    """

    def allow_request(self, request, view):
        if request.method == "POST":
            return super().allow_request(request, view)
        return True
