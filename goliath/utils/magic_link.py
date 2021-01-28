from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.http import urlquote
from sesame.utils import get_query_string
from django.contrib.sites.shortcuts import get_current_site


def send_magic_link(request, user, email, viewname):
    """
    Sending the email via django's send_mail because we do need the special features of anymail.
    """
    magic_link = settings.URL_ORIGIN + (
        reverse(viewname)
        + get_query_string(user, scope=email)
        + "&email="
        + urlquote(email)
    )

    context = {"activate_url": magic_link, "current_site": get_current_site(request)}

    subject = render_to_string("account/email/email_confirmation_subject.txt")
    body_text = render_to_string(
        "account/email/email_confirmation_message.txt",
        context,
    )
    body_html = render_to_string(
        "account/email/email_confirmation_message.html",
        context,
    )

    send_mail(
        subject,
        body_text,
        settings.DEFAULT_FROM_EMAIL,
        [email],
        html_message=body_html,
    )
