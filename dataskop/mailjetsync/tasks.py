from datetime import timedelta

from allauth.account.models import EmailAddress
from celery import shared_task
from django.utils import timezone

from dataskop.campaigns.models import Donation, Event
from dataskop.mailjetsync.api.serializers import NewsletterSubscriptionSerializer
from dataskop.mailjetsync.mailjet import subscribe_mailjet_list
from dataskop.mailjetsync.models import NewsletterSubscription


@shared_task(queue="high_priority", acks_late=True, reject_on_worker_lost=True)
def handle_newsletter_subscription(request_data, ip_address):
    """
    Process POSTed data.
    """
    if not isinstance(request_data, dict):
        Event.objects.create(
            message="Data for newletter subscription is faulty",
            data={"post_data": request_data},
        )
        return

    request_data["ip_address"] = ip_address
    serializer = NewsletterSubscriptionSerializer(data=request_data)
    if serializer.is_valid():
        serializer.save()
    else:
        # Check if the same email was used already to subscribe to the newsletter.
        if NewsletterSubscription.objects.filter(
            email=serializer.data["email"]
        ).exists():
            Event.objects.create(
                message="Newsletter subscription: email duplicated",
                data={"errors": serializer.errors, "post_data": request_data},
            )
        else:
            Event.objects.create(
                message="Newsletter subscription: serializer failed",
                data={"errors": serializer.errors, "post_data": request_data},
            )


@shared_task(
    queue="low_priority",
    rate_limit="5/s",
    autoretry_for=(Exception,),
    retry_backoff=True,
)
def add_to_mailjet(email, has_donated):
    """
    Add email address to Mailjet List
    """
    try:
        subscribe_mailjet_list(email, has_donated)
    except Exception as e:
        Event.objects.create(
            message="Problem with Mailjet API",
            data={"email": email, "error_message": str(e)},
        )
        raise e


@shared_task(
    queue="low_priority",
)
def enqueue_confirmed_emails():
    """
    Check for emails that don't need a double opt-in confirmation and add them.
    """
    the_past = timezone.now() - timedelta(days=7)
    user_pks_with_recent_confirmed_donation = set(
        Donation.objects.confirmed()
        .filter(confirmed_at__gte=the_past)
        .values_list("donor", flat=True)
    )

    for n in NewsletterSubscription.objects.filter(
        needs_double_optin=False, confirmed_at__isnull=True
    ):
        email_obj = EmailAddress.objects.filter(email=n.email)
        if email_obj.user.pk in user_pks_with_recent_confirmed_donation:
            add_to_mailjet.delay(n.email, n.has_donated)
            n.confirmed_at = timezone.now()
            n.save()
