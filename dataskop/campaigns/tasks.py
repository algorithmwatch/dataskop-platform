"""
Celery tasks to off-load certain funtionality.

We are currently using two queues (high_priority and low_priority). In a simple setup,
a single worker should consume tasks from both queues. This ensures that low priority
tasks don't block the high priority tasks (since tasks from the queues are fetched in
a round robin way).
"""
import json
import subprocess

from celery import current_app, shared_task
from django.contrib.sites.models import Site
from herald.models import SentNotification

from dataskop.campaigns.api.serializers import (
    DonationUnauthorizedSerializer,
    EventSerializer,
)
from dataskop.campaigns.models import Donation, Event
from dataskop.campaigns.notifications import DonorNotificationEmail, ReminderEmail
from dataskop.users.models import User
from dataskop.utils.email import send_admin_notification


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
    if not isinstance(request_data, dict):
        Event.objects.create(
            message="Data for unauthorized donation is faulty",
            data={"post_data": request_data},
        )
        return

    request_data["ip_address"] = ip_address
    serializer = DonationUnauthorizedSerializer(data=request_data)
    if serializer.is_valid():
        serializer.save()
    else:
        Event.objects.create(
            message="Serialzer for unauthorized donation failed",
            data={"errors": serializer.errors, "post_data": request_data},
        )


@shared_task(queue="low_priority", acks_late=True, reject_on_worker_lost=True)
def handle_event(request_data, ip_address):
    """
    Process POSTed data to create an event.
    """
    if not isinstance(request_data, dict):
        Event.objects.create(
            message="Data for event is faulty",
            data={"post_data": request_data},
        )
        return

    request_data["ip_address"] = ip_address
    serializer = EventSerializer(data=request_data)
    if serializer.is_valid():
        serializer.save()
    else:
        Event.objects.create(
            message="serialzer for event failed",
            data={"errors": serializer.errors, "post_data": request_data},
        )


@shared_task(queue="low_priority", acks_late=True, reject_on_worker_lost=True)
def add_event(message, data):
    Event.objects.create(
        message=message,
        data=data,
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
    retry_backoff=True,
)
def send_reminder_email(user_pk, site_pk):
    user = User.objects.get(pk=user_pk)
    site = Site.objects.get(pk=site_pk)
    ReminderEmail(user, site).send(user=user, raise_exception=True)


@shared_task(
    queue="high_priority",
    rate_limit="5/s",
    autoretry_for=(Exception,),
    retry_backoff=True,
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
    Test if celery beat only runs once to prevent duplicate emails and get some
    information.
    """
    celery_stats = f"celery:\n\n\
{json.dumps(current_app.control.inspect().stats(), sort_keys=True, indent=4)}"

    # For FreeBSD: https://raghukumarc.blogspot.com/2011/11/show-all-processes-in-freebsd.html
    ps = subprocess.run(["ps", "-auxww"], capture_output=True, text=True).stdout.strip(
        "\n"
    )

    send_admin_notification(
        "DataSkop Heartbeat",
        f"This email should only be sent once. If not, please contact the developer.\
\n\n{celery_stats}\n\nps:\n\n{ps}",
    )
