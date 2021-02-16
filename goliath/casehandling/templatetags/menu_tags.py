from django import template
from django.urls import reverse

register = template.Library()


def create_user_menu(is_authenticated):
    return (
        [
            {"label": "Meine Anliegen", "url": reverse("cases"), "is_user_menu": True},
            {
                "label": "Mein Account",
                "url": reverse("account_index"),
                "is_user_menu": True,
            },
            {
                "label": "Log out",
                "url": reverse("account_logout"),
                "is_user_menu": True,
            },
        ]
        if is_authenticated is True
        else [
            {"label": "Login", "url": reverse("account_login"), "is_user_menu": True},
            {
                "label": "Registrieren",
                "url": reverse("account_signup"),
                "is_user_menu": True,
            },
        ]
    )


@register.simple_tag(takes_context=True)
def primary_menu(context, mobile=True):
    request = context.get("request", None)

    if not request:
        return []

    if mobile is True:
        site_menu = [
            {
                "label": "Unding melden",
                "url": "/neu/",
            },
            {
                "label": "Dashboard",
                "url": "/dashboard.html",
            },
            {
                "label": "Über uns",
                "url": "/ueber-uns.html",
            },
        ]

        if request.user.is_authenticated:
            result = create_user_menu(True) + site_menu

        else:
            result = site_menu + create_user_menu(False)

        return result

    else:
        site_menu = [
            {
                "label": "Dashboard",
                "url": "/dashboard.html",
            },
            {
                "label": "Über uns",
                "url": "/ueber-uns.html",
            },
        ]

        report_button = {"label": "Unding melden", "url": "/neu/", "is_button": True}

        if request.user.is_authenticated:
            result = site_menu
        else:
            result = site_menu + create_user_menu(False)

        result.append(report_button)

        return result


@register.simple_tag(takes_context=True)
def user_menu(context):
    request = context.get("request", None)

    if not request:
        return []

    return create_user_menu(request.user.is_authenticated is True)
