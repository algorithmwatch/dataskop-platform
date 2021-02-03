from anymail.message import AnymailMessage
from django.conf import settings
from django.contrib.sites.models import Site
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.http import urlquote
from sesame.utils import get_query_string


def send_anymail_email(to_email, text_content, html_content=None, **kwargs):
    """
    Sending generic email with anymail + returns id & status
    """
    context = {"message": text_content, "current_site": Site.objects.get_current()}

    body_text = render_to_string(
        "account/email/generic_message.txt",
        context,
    )

    if html_content is not None:
        context["message"] = html_content

    body_html = render_to_string(
        "account/email/generic_message.html",
        context,
    )

    msg = AnymailMessage(body=body_text, **kwargs, to=[to_email])
    msg.attach_alternative(body_html, "text/html")
    msg.send()

    status = msg.anymail_status  # available after sending
    esp_message_id = status.message_id  # e.g., '<12345.67890@example.com>'

    # can only be None during debug, don't run this section in debug?
    esp_message_status = None
    if to_email in status.recipients:
        esp_message_status = status.recipients[to_email].status  # e.g., 'queued'
    return esp_message_id, esp_message_status


def send_magic_link(user, email, viewname):
    """
    Sending the email via django's send_mail because we do need the special features of anymail.
    """
    magic_link = settings.URL_ORIGIN + (
        reverse(viewname)
        + get_query_string(user, scope=email)
        + "&email="
        + urlquote(email)
    )

    context = {"activate_url": magic_link, "current_site": Site.objects.get_current()}

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
