from datetime import timedelta

from allauth.account.models import EmailAddress
from autoslug import AutoSlugField
from django.contrib.auth import get_user_model
from django.db import models
from django.urls.base import reverse
from django.utils import timezone
from django_lifecycle import AFTER_CREATE, LifecycleModel, hook
from herald.models import SentNotification
from model_utils import Choices
from model_utils.fields import StatusField
from model_utils.models import TimeStampedModel
from simple_history.models import HistoricalRecords

from dataskop.campaigns.managers import DonationManagers
from dataskop.campaigns.notifications import UnauthorizedDonationShouldLoginEmail

User = get_user_model()

# https://github.com/jazzband/django-simple-history/issues/190#issuecomment-134281202
class StatusOptions(object):
    STATUS_OPTIONS = Choices("draft", "active", "inactive")


class Provider(TimeStampedModel):
    name = models.CharField(max_length=255)
    scraping_config_schema = models.JSONField(null=True, blank=True)

    def __str__(self) -> str:
        return self.name


class Campaign(StatusOptions, TimeStampedModel):
    status = StatusField(choices_name="STATUS_OPTIONS")
    title = models.CharField(max_length=255)
    slug = AutoSlugField(populate_from="title")
    description = models.TextField(null=True, blank=True)
    created_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True
    )
    scraping_config = models.JSONField(null=True, blank=True)
    image = models.ImageField(null=True, blank=True, upload_to="campaigns")
    provider = models.ForeignKey(
        "Provider", on_delete=models.SET_NULL, null=True, blank=True
    )
    history = HistoricalRecords(bases=[StatusOptions, TimeStampedModel])

    class Meta:
        permissions = (("assign_campaign", "Assign campaign"),)

    def __str__(self) -> str:
        return self.title


class Donation(LifecycleModel, TimeStampedModel):
    campaign = models.ForeignKey(
        "Campaign", on_delete=models.SET_NULL, null=True, blank=True
    )
    # delete all donations when users delete their account
    donor = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    results = models.JSONField(null=True, blank=True)
    unauthorized_email = models.EmailField(null=True, blank=True)

    objects = DonationManagers()

    def __str__(self) -> str:
        return f"{self.campaign} / {self.created} / {self.donor} / {self.unauthorized_email}"

    def get_absolute_url(self):
        return reverse("my_donations_detail", kwargs={"pk": self.pk})

    @hook(AFTER_CREATE, when="unauthorized_email", is_not=None)
    def after_creattion_with_unauthorized_email(self):
        assert self.donor is None

        existing_email = EmailAddress.objects.filter(
            email=self.unauthorized_email
        ).first()

        if existing_email:
            recenttime = timezone.now() - timedelta(hours=2)
            thefuture = timezone.now() + timedelta(hours=2)

            num_recent_sent = SentNotification.objects.filter(
                user=existing_email.user, date_sent__range=(recenttime, thefuture)
            ).count()

            if num_recent_sent == 0:
                UnauthorizedDonationShouldLoginEmail(existing_email.user).send(
                    user=existing_email.user, raise_exception=True
                )
        else:
            User.objects.create_unverified_user_send_mail(self.unauthorized_email)
