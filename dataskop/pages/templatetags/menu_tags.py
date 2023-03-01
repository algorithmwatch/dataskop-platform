from typing import List, TypedDict

from django import template
from django.urls import reverse

register = template.Library()


def create_user_menu(is_authenticated):
    return (
        [
            {
                "label": "Meine Spenden",
                "url": reverse("my_donations_list"),
                "is_user_menu": True,
            },
            {
                "label": "Mein Konto",
                "url": reverse("account_index"),
                "is_user_menu": True,
            },
            {
                "label": "Abmelden",
                "url": reverse("account_logout"),
                "is_user_menu": True,
            },
        ]
        if is_authenticated is True
        else [
            {"label": "Login", "url": reverse("account_login"), "is_user_menu": True},
            # {
            #     "label": "Registrieren",
            #     "url": reverse("account_signup"),
            #     "is_user_menu": True,
            # },
        ]
    )


class MenuItem(TypedDict):
    label: str
    url: str


@register.simple_tag(takes_context=True)
def primary_menu(context, mobile=True):
    request = context.get("request", None)

    if not request:
        return []

    site_menu: List[MenuItem]
    if mobile is True:
        site_menu = [
            # {
            #     "label": "Start",
            #     "url": reverse("home"),
            # },
        ]

        if request.user.is_authenticated:
            result = create_user_menu(True) + site_menu

        else:
            result = site_menu + create_user_menu(False)

        return result

    else:
        site_menu = [
            # {
            #     "label": "Start",
            #     "url": reverse("home"),
            # },
        ]

        if request.user.is_authenticated:
            result = site_menu
        else:
            result = site_menu + create_user_menu(False)

        return result


@register.simple_tag(takes_context=True)
def user_menu(context):
    request = context.get("request", None)

    if not request:
        return []

    return create_user_menu(request.user.is_authenticated is True)
