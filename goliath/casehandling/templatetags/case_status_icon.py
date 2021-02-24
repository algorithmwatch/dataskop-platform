from django import template

from ..models import Case

register = template.Library()


@register.simple_tag
def case_status_icon(status):
    icon_map = {
        "WAITING_EMAIL_ERROR": "fas fa-times",
        "WAITING_USER_VERIFIED": "fas fa-user-clock",
        "WAITING_CASE_APPROVED": "",
        "WAITING_INITIAL_EMAIL_SENT": "fas fa-paper-plane",
        "WAITING_RESPONSE": "fas fa-clock",
        "WAITING_USER_INPUT": "fas fa-bell",
        "CLOSED_NEGATIVE": "fas fa-thumbs-down",
        "CLOSED_POSITIVE": "fas fa-thumbs-up",
    }

    for key, icon_name in icon_map.items():
        status_value = getattr(Case.Status, key, None)

        if status_value and status_value == status:
            return icon_name

    return ""
