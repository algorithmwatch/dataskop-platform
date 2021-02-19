from allauth.account.signals import email_confirmed
from anymail.signals import inbound
from django.conf import settings
from django.contrib.auth import get_user_model
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django_comments.signals import comment_was_posted

from .models import Case, ReceivedMessage
from .tasks import persist_inbound_email, send_admin_new_comment, send_initial_emails

User = get_user_model()


@receiver(inbound)  # add weak=False if inside some other function/class
def handle_inbond_email(sender, event, esp_name, **kwargs):
    persist_inbound_email(event.message)


@receiver(email_confirmed)
def handle_email_confirmed(request, email_address, **kwargs):
    """
    Used when verifying an email adress via django all auth
    """
    user = User.objects.get(email=email_address.email)

    for c in Case.objects.filter(user=user):
        c.user_verified_afterwards()


@receiver(comment_was_posted)
def post_comment(**kwargs):
    send_admin_new_comment()
