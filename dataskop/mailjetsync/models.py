from django.contrib.sites.models import Site
from django.db import models
from django.utils import timezone
from django_lifecycle import AFTER_CREATE, LifecycleModelMixin, hook
from model_utils.models import TimeStampedModel

from dataskop.mailjetsync.notifications import MailjetsyncSubscribe
from dataskop.users.models import User


class NewsletterSubscription(LifecycleModelMixin, TimeStampedModel):
    """
    Sync emails to a Mailjet list. If required, send out a double optin mail.
    """

    email = models.EmailField(unique=True)
    needs_double_optin = models.BooleanField()
    has_donated = models.BooleanField()
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    confirmed_at = models.DateTimeField(null=True, blank=True)
    token = models.CharField(max_length=20, null=True, blank=True)

    def __str__(self) -> str:
        return self.id

    @hook(AFTER_CREATE, when="needs_double_optin", is_now=True)
    def send_double_optin_mail(self):
        token = User.objects.make_random_password(20)
        self.token = token
        self.save()
        MailjetsyncSubscribe(token, self.email, Site.objects.first()).send()

    def confirm(self):
        from dataskop.mailjetsync.tasks import add_to_mailjet

        self.confirmed_at = timezone.now()
        self.save()
        add_to_mailjet.delay(self.email, self.has_donated)
