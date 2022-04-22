"""
Celery tasks to off-load certain funtionality.

We are currently using two queues (high_priority and low_priority). In a simple setup,
a single worker should consume tasks from both queues. This ensures that low priority
tasks don't block the high priority tasks (since tasks from the queues are fetched in
a round robin way).
"""
from celery import shared_task
from django.contrib.auth import get_user_model
from django.contrib.sites.models import Site
from herald.models import SentNotification

from dataskop.campaigns.api.serializers import (
    DonationUnauthorizedSerializer,
    EventSerializer,
)
from dataskop.campaigns.models import Donation, Event
from dataskop.campaigns.notifications import DonorNotificationEmail, ReminderEmail
from dataskop.utils.email import send_admin_notification

User = get_user_model()


@shared_task(queue="high_priority", acks_late=True, reject_on_worker_lost=True)
def handle_donation(request_data, ip_address):
    """
    Process POSTed data to create a donation.

    We don't enforce atomic requests because it's unlikely that an exception gets thrown
    due to external factors. If there is an exception, there is most likely a bug. And,
    we want to make sure that the donation gets persisted to the DB. All the post-save
    handling of a donation is not essential. In the worst case, we have to retry a task
    and a donation gets duplicated (and this can be handled manually). All bugs get
    reported via sentry.

    On `acks_late` and `reject_on_worker_lost`: We want to make sure that we don't miss
    any kind of donation. If something is wrong with the worker, the donation is still
    in the queue.
    """
    request_data["ip_address"] = ip_address
    serializer = DonationUnauthorizedSerializer(data=request_data)
    if serializer.is_valid():
        serializer.save()
    else:
        Event.objects.create(
            message="serialzer for unauthorized donation failed",
            data={"errors": serializer.errors, "post_data": request_data},
        )


@shared_task(queue="low_priority", acks_late=True, reject_on_worker_lost=True)
def handle_event(request_data, ip_address):
    """
    Process POSTed data to create an event.
    """
    request_data["ip_address"] = ip_address
    serializer = EventSerializer(data=request_data)
    if serializer.is_valid():
        serializer.save()
    else:
        Event.objects.create(
            message="serialzer for event failed",
            data={"errors": serializer.errors, "post_data": request_data},
        )


@shared_task(queue="high_priority")
def remind_user_registration():
    """
    Send reminder emails to users who didn't verify their email address.
    """
    num_reminder_sent = Donation.objects.remind_user_registration()
    if num_reminder_sent > 0:
        text = f"{num_reminder_sent} reminders sent"
        send_admin_notification(text, text)
    return num_reminder_sent


@shared_task(
    queue="low_priority",
    rate_limit="5/s",
    autoretry_for=(Exception,),
    retry_backoff=3,
    retry_kwargs={"max_retries": 5},
)
def send_reminder_email(user_pk, site_pk):
    user = User.objects.get(pk=user_pk)
    site = Site.objects.get(pk=site_pk)
    ReminderEmail(user, site).send(user=user, raise_exception=True)


@shared_task(
    queue="high_priority",
    rate_limit="5/s",
    autoretry_for=(Exception,),
    retry_backoff=3,
    retry_kwargs={"max_retries": 5},
)
def send_donor_notification_email(user_pk, subject, text, campaign_pk):
    user = User.objects.get(pk=user_pk)
    DonorNotificationEmail(user, subject, text, campaign_pk).send(
        user=user, raise_exception=True
    )


@shared_task(queue="low_priority")
def resend_failed_emails():
    """
    Try to resend some failed emails.
    """
    notification_types = (
        "ConfirmedRegistrationEmail",
        "UnauthorizedDonationShouldLoginEmail",
    )

    for nt in notification_types:
        for sn in SentNotification.objects.filter(
            status=SentNotification.STATUS_FAILED,
            notification_class=f"dataskop.campaigns.notifications.{nt}",
        ):
            sn.resend()


@shared_task(queue="low_priority")
def test_task_email():
    """
    Test if celery beat only runs once to prevent duplicate emails.
    """
    send_admin_notification(
        "Test task e-mail",
        "this E-Mail should only be sent once.",
    )
