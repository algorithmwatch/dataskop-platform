import datetime

from anymail.message import AnymailMessage

from config import celery_app

from .models import SentMessage


@celery_app.task()
def send_email(case, subject, content):
    """Sent email."""

    from_email, to_email = case.email, case.entity.email

    text_content = content
    html_content = f"<p>{content}</p>"
    msg = AnymailMessage(subject, text_content, from_email, [to_email])
    msg.attach_alternative(html_content, "text/html")
    msg.send()

    status = msg.anymail_status  # available after sending
    esp_message_id = status.message_id  # e.g., '<12345.67890@example.com>'
    esp_message_status = status.recipients[to_email].status  # e.g., 'queued'

    error_message = None
    if esp_message_status not in ("sent", "queued"):
        error_message = esp_message_status

    SentMessage.objects.create(
        case=case,
        to_email=to_email,
        from_email=from_email,
        subject=subject,
        content=content,
        esp_message_id=esp_message_id,
        esp_message_status=esp_message_status,
        error_message=error_message,
        sent_at=datetime.datetime.now(),
    )
