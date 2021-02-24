def per_user(group, request):
    if request.user.is_authenticated:
        if request.user.is_staff:
            return "10000/h"
        return "5/h"
    return "10/h"
