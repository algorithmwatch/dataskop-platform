import datetime

from anymail.message import AnymailMessage

from config import celery_app

from .models import SentMessage, Case, ReceivedMessage

# to avoid DB lookups
BASE_DOMAIN = "https://lab2.algorithmwatch.org"


def _send_email(to_email, html_content, *kwargs):
    """Send email."""
    msg = AnymailMessage(*kwargs, [to_email])
    msg.attach_alternative(html_content, "text/html")
    msg.send()

    status = msg.anymail_status  # available after sending
    esp_message_id = status.message_id  # e.g., '<12345.67890@example.com>'

    # can only be None during debug, don't run this section in debug?
    esp_message_status = None
    if to_email in status.recipients:
        esp_message_status = status.recipients[to_email].status  # e.g., 'queued'
    return esp_message_id, esp_message_status


@celery_app.task()
def send_initial_email(case, subject, content):
    """Initial email"""
    from_email, to_email = case.email, case.entity.email
    text_content = content
    html_content = f"<p>{content}</p>"

    esp_message_id, esp_message_status = _send_email(
        to_email, html_content, subject, text_content, from_email
    )

    error_message = None
    if esp_message_status not in ("sent", "queued"):
        error_message = esp_message_status

    # TODO: update or create
    SentMessage.objects.create(
        case=case,
        to_email=to_email,
        from_email=from_email,
        subject=subject,
        content=content,
        esp_message_id=esp_message_id,
        esp_message_status=esp_message_status,
        error_message=error_message,
        sent_at=datetime.datetime.utcnow(),
    )


@celery_app.task()
def send_notifical_email(to_email, from_email, subject, content):
    """Send email."""
    text_content = content
    html_content = f"<p>{content}</p>"
    _send_email(to_email, html_content, subject, text_content, from_email)


@celery_app.task()
def persist_inbound_email(message):
    all_to_addresses = [x.addr_spec for x in message.to] + [message.envelope_recipient]

    to_address, case = None, None
    for x in all_to_addresses:
        # can be None
        case = Case.objects.filter(email=x).first()
        if case is not None:
            to_address = x
            break

    msg = ReceivedMessage.objects.create(
        case=case,
        from_email=message.envelope_sender,
        to_email=to_address,
        content=message.text,
        html=message.html,
        subject=message.subject,
        sent_at=message.date,
        spam_score=message.spam_score,
        from_display_name=message.from_email.display_name
        if message.from_email is not None
        else None,
        from_display_email=message.from_email.addr_spec
        if message.from_email is not None
        else None,
        received_at=datetime.datetime.utcnow(),
        to_addresses=[str(x) for x in message.to] + [message.envelope_recipient],
        cc_addresses=[str(x) for x in message.cc],
    )

    if case is not None:
        send_notifical_email(
            case.user.email,
            "info@aw.jfilter.de",
            "Neue Antwort auf Goliath",
            "Hallo, Sie haben eine neue E-Mai auf Goliath.\n\n"
            + BASE_DOMAIN
            + case.get_absolute_url(),
        )
