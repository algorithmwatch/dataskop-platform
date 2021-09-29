from anymail.message import AnymailMessage
from django.conf import settings


def send_admin_notifcation(subject, text):
    to_email = settings.ADMIN_NOTIFICATION_EMAIL
    msg = AnymailMessage(body=text, subject=subject, to=[to_email])
    msg.send()

    status = msg.anymail_status  # available after sending
    esp_message_id = status.message_id  # e.g., '<12345.67890@example.com>'

    # can only be None during debug, don't run this section in debug?
    esp_message_status = None
    if to_email in status.recipients:
        esp_message_status = status.recipients[to_email].status  # e.g., 'queued'
    return esp_message_id, esp_message_status
