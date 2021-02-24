import datetime

from django.conf import settings
from django.urls import reverse
from email_reply_parser import EmailReplyParser

from config import celery_app

from ..utils.email import send_anymail_email
from .models import Case, ReceivedMessage, SentMessage


@celery_app.task()
def send_initial_emails_to_entities(postCC):
    """
    send initial email to entity of case type
    """

    num_mails = 0
    all_success = True
    for case in postCC.cases.all():
        subject = case.answers_subject
        content = case.answers_text

        assert (
            case.is_sane
        ), f"can't send email because the case is broken, case id: {case.id}"

        to_emails = list(case.selected_entities.values_list("email", flat=True))
        assert (
            len(to_emails) > 0
        ), f"at least one entity needs to be selected, case id: {case.id}"

        was_error = False

        for to_email in to_emails:
            print("sending to", to_email)
            from_email = case.email

            esp_message_id, esp_message_status = send_anymail_email(
                to_email,
                subject=subject,
                from_email=from_email,
                text_content=content,
                is_generic=False,
            )

            error_message = None
            if esp_message_status not in ("sent", "queued"):
                error_message = esp_message_status

            if error_message is not None:
                was_error = True

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

        if was_error:
            case.status = Case.Status.WAITING_EMAIL_ERROR
        else:
            # all good, waiting for response
            case.status = Case.Status.WAITING_RESPONSE
        case.save()
        num_mails += 1
        if all_success:
            all_success = not was_error

    if all_success:
        text = f"wir haben {num_mails} Nachrichten versandt."
        ctaLabel = "zu den Fällen"
        ctaLink = reverse("cases")
        if num_mails == 1:
            text = "wir haben eine Nachricht versandt."
            ctaLink = settings.URL_ORIGIN + postCC.cases.first().get_absolute_url()

        send_anymail_email(
            postCC.user.email,
            text,
            from_email=settings.DEFAULT_FROM_EMAIL,
            subject="E-Mails erfolgreich versandt",
            ctaLink=ctaLink,
            ctaLabel=ctaLabel,
        )

        postCC.sent_initial_emails_at = datetime.datetime.utcnow()
        postCC.save()

    else:
        # something went wrong, notify admins
        send_admin_notification_email(
            "error sending email", f"checkout postcc: {postCC.pk}"
        )


@celery_app.task()
def send_user_notification_new_message(to_email, link, text):
    """Notify user about incoming new email"""
    send_anymail_email(
        to_email,
        text,
        from_email=settings.DEFAULT_FROM_EMAIL,
        subject="Neue Antwort",
        ctaLink=link,
        ctaLabel="zur Antwort",
    )


@celery_app.task()
def send_user_notification_reminder(to_email, link):
    """Remind user about open case"""
    send_anymail_email(
        to_email,
        "Bitte setzen Sie den Status",
        from_email=settings.DEFAULT_FROM_EMAIL,
        subject="Bitte setzen Sie den Status",
        ctaLink=link,
    )


@celery_app.task()
def send_user_notification_new_comment(to_email, link):
    """Inform user about new comment"""
    send_anymail_email(
        to_email,
        "Neuer Kommentar zu Ihrem Fall",
        from_email=settings.DEFAULT_FROM_EMAIL,
        subject="Neuer Kommentar zu Ihrem Fall",
        ctaLink=link,
    )


@celery_app.task()
def send_entity_notification_reminder(to_email, from_email):
    """Remind user about open case"""
    send_anymail_email(
        to_email,
        "Bitte Antworten Sie auf unsere Anfrage",
        from_email=from_email,
        subject="Bitte Antworten Sie auf unsere Anfrage",
    )


@celery_app.task()
def send_admin_notification_email(subject, content):
    to_email = settings.ADMIN_NOTIFICATION_EMAIL
    from_email = settings.DEFAULT_FROM_EMAIL
    send_anymail_email(
        to_email, subject=subject, text_content=content, from_email=from_email
    )


def send_admin_notification_waiting_approval_case():
    send_admin_notification_email(
        "Neuer Fall benötigt eine Freigabe",
        settings.URL_ORIGIN
        + "/"
        + settings.ADMIN_URL
        + "casehandling/case/?approval=needs_approval",
    )


def send_admin_notification_new_comment():
    send_admin_notification_email(
        "Neuer Kommentar",
        settings.URL_ORIGIN + "/" + settings.ADMIN_URL + "django_comments/comment/",
    )


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

    case_found = case is not None
    parsed_content = EmailReplyParser.parse_reply(message.text)
    is_autoreply = None
    if case_found:
        is_autoreply = case.case_type.is_message_autoreply(parsed_content)

    ReceivedMessage.objects.create(
        case=case,
        from_email=message.envelope_sender,
        to_email=to_address,
        content=message.text,
        parsed_content=parsed_content,
        is_autoreply=is_autoreply,
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
        case.handle_incoming_email(is_autoreply)
