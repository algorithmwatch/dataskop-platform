# mypy: ignore-errors
# add anymails status to herald's `extra_data`

import json
from email.mime.base import MIMEBase

import six
from anymail.message import AnymailMessage
from django.utils import timezone

EmailMultiAlternatives = AnymailMessage


def _send(
    recipients,
    text_content=None,
    html_content=None,
    sent_from=None,
    subject=None,
    extra_data=None,
    attachments=None,
):
    extra_data = extra_data or {}

    mail = EmailMultiAlternatives(
        subject=subject,
        body=text_content,
        from_email=sent_from,
        to=recipients,
        bcc=extra_data.get("bcc", None),
        headers=extra_data.get("headers", None),
        cc=extra_data.get("cc", None),
        reply_to=extra_data.get("reply_to", None),
    )

    if html_content:
        mail.attach_alternative(html_content, "text/html")

    for attachment in attachments or []:
        # All mimebase attachments must have a Content-ID or Content-Disposition header
        # or they will show up as unnamed attachments"
        if isinstance(attachment, MIMEBase):
            if attachment.get("Content-ID", False):
                # if you are sending attachment with content id,
                # subtype must be 'related'.
                mail.mixed_subtype = "related"

            mail.attach(attachment)
        else:
            mail.attach(*attachment)

    mail.send()
    status = mail.anymail_status
    try:
        return {
            "id": status.message_id,
            "status": json.dumps([status.recipients[r].status for r in recipients]),
        }
    except:
        return {"id": None, "status": "not possible to parse anymail response"}


def resend(cls, sent_notification, raise_exception=False):
    """
    Takes a saved sent_notification and sends it again.
    returns boolean whether or not the notification was sent successfully
    """

    # handle skipping a notification based on user preference
    if hasattr(sent_notification.user, "usernotification"):
        notifications = sent_notification.user.usernotification
        if notifications.disabled_notifications.filter(
            notification_class=cls.get_class_path()
        ).exists():
            sent_notification.date_sent = timezone.now()
            sent_notification.status = sent_notification.STATUS_USER_DISABLED
            sent_notification.save()
            return True

    try:
        anymailstatus = cls._send(
            sent_notification.get_recipients(),
            sent_notification.text_content,
            sent_notification.html_content,
            sent_notification.sent_from,
            sent_notification.subject,
            sent_notification.get_extra_data(),
            sent_notification.get_attachments(),
        )
        sent_notification.status = sent_notification.STATUS_SUCCESS
        updated_extra_data = sent_notification.get_extra_data()
        updated_extra_data["anymailstatus"] = anymailstatus

        sent_notification.extra_data = json.dumps(updated_extra_data)

    except Exception as exc:  # pylint: disable=W0703
        # we want to handle any exception whatsoever
        sent_notification.status = sent_notification.STATUS_FAILED
        sent_notification.error_message = six.text_type(exc)

        if raise_exception:
            raise exc

    sent_notification.date_sent = timezone.now()
    sent_notification.save()

    cls._delete_expired_notifications()

    return sent_notification.status == sent_notification.STATUS_SUCCESS
