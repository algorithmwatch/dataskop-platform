from django.conf import settings
from rest_framework.throttling import ScopedRateThrottle


class PostScopedRateThrottle(ScopedRateThrottle):
    """
    Only throttle post requests.
    """

    def allow_request(self, request, view):
        # Optionally disable throttle
        if not settings.RATELIMIT_ENABLE:
            return True

        if request.method == "POST":
            return super().allow_request(request, view)
        return True
