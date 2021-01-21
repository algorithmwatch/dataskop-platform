from django.conf import settings
from django.core.mail import send_mail
from django.urls import reverse
from django.utils.http import urlquote
from sesame.utils import get_query_string


def send_magic_link(user, email, viewname):
    magic_link = settings.URL_ORIGIN + (
        reverse(viewname)
        + get_query_string(user, scope=email)
        + "&email="
        + urlquote(email)
    )

    send_mail(
        "Email Login",
        "Click the link " + magic_link,
        "noreply@aw.jfilter.de",
        [email],
        html_message=f"""<html><a href="{magic_link}">Click the link to login</a></html>""",
    )
