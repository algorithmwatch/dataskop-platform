from .models import Ratelimit


def per_user(group, request):
    if request.user.is_authenticated:
        return "5/h"
    return "10/h"
