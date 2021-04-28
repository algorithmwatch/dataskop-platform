from allauth.account.models import EmailAddress
from allauth.account.signals import email_confirmed
from anymail.signals import inbound
from django.conf import settings
from django.contrib.auth import get_user_model
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django_comments.signals import comment_was_posted

from .models import Case, PostCaseCreation, ReceivedMessage
from .tasks import (
    persist_inbound_email,
    send_admin_notification_new_comment,
    send_user_notification_new_comment,
)

User = get_user_model()


@receiver(inbound)  # add weak=False if inside some other function/class
def handle_inbond_email(sender, event, esp_name, **kwargs):
    persist_inbound_email(event.message)


@receiver(email_confirmed)
def handle_email_confirmed(request, email_address, **kwargs):
    """
    Used when verifying an email adress via django all auth
    """
    user = email_address.user
    for c in PostCaseCreation.objects.filter(user=user):
        c.user_verified_afterwards()


@receiver(comment_was_posted)
def post_comment(sender, **kwargs):
    instance = kwargs["comment"]
    # was comment posted by staff? if yes: inform user about new comment
    if instance.user.is_staff:
        comment_user = instance.content_object.case.user
        user_email = comment_user.email
        user_name = comment_user.full_name
        link = (
            settings.URL_ORIGIN
            + instance.content_object.case.get_absolute_url()
            + "#c"
            + str(instance.pk)
        )

        send_user_notification_new_comment(user_email, link, user_name)

    # always inform
    send_admin_notification_new_comment()
