import time
from datetime import timedelta

from allauth.account.models import EmailAddress
from autoslug import AutoSlugField
from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import models
from django.db.models import Q
from django.urls.base import reverse
from django.utils import timezone
from django_lifecycle import (
    AFTER_CREATE,
    LifecycleModel,
    hook,
    AFTER_SAVE,
    AFTER_UPDATE,
    BEFORE_DELETE,
)
from herald.models import SentNotification
from model_utils import Choices
from model_utils.fields import StatusField
from model_utils.models import TimeStampedModel
from simple_history.models import HistoricalRecords

from dataskop.campaigns.managers import DonationManager
from dataskop.campaigns.notifications import (
    DonorNotificationEmail,
    UnauthorizedDonationShouldLoginEmail,
)
from dataskop.utils.email import send_admin_notifcation

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
    # store ip address only until the user is verified
    ip_address = models.GenericIPAddressField(null=True, blank=True)

    objects = DonationManager()

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
                user=existing_email.user,
                date_sent__range=(recenttime, thefuture),
                notification_class="dataskop.campaigns.notifications.UnauthorizedDonationShouldLoginEmail",
            ).count()

            if num_recent_sent == 0:
                UnauthorizedDonationShouldLoginEmail(existing_email.user).send(
                    user=existing_email.user, raise_exception=True
                )
        else:
            User.objects.create_unverified_user_send_mail(
                self.unauthorized_email, self.ip_address
            )

    @hook(BEFORE_DELETE)
    def send_admin_notification_before_delete(self):
        send_admin_notifcation(
            "Donation Deleted",
            f"Donation with id {self.pk}, for campaign {self.campaign}, was deleted",
        )


class Event(TimeStampedModel):
    campaign = models.ForeignKey(
        "Campaign", on_delete=models.SET_NULL, null=True, blank=True
    )
    message = models.CharField(max_length=100, null=True, blank=True)
    data = models.JSONField(null=True, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)

    def __str__(self) -> str:
        return f"{self.created} / {self.message} / {self.ip_address}"


class DonorNotificationSetting(TimeStampedModel):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
    )
    disable_all = models.BooleanField(default=False)
    # user's can manually opt-out of notifications for a specific campaign
    disabled_campaigns = models.ManyToManyField("Campaign", blank=True)


class DonorNotification(LifecycleModel, TimeStampedModel):
    # NB: `sent_by` and `campaign` can't be blank in the admin form
    sent_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=False)
    draft = models.BooleanField(
        default=True,
        help_text="If you set draft to false, the email will get sent to the chosen campaign (and can't be changed anymore).",
    )
    subject = models.CharField(max_length=255)
    text = models.TextField()
    campaign = models.ForeignKey(
        "Campaign",
        on_delete=models.SET_NULL,
        null=True,
        blank=False,
        help_text="Which campaign should receive this message?",
    )

    def __str__(self) -> str:
        return f"{self.subject[:20]} / {self.campaign} / {self.sent_by}"

    def send_notification(self):
        users = User.objects.filter(
            pk__in=(
                self.campaign.donation_set.confirmed().values_list("donor").distinct()
            )
        )

        exclude_users = DonorNotificationSetting.objects.filter(
            Q(disable_all=True) | Q(disabled_campaigns=self.campaign)
        ).values_list("user")

        for u in users.exclude(pk__in=exclude_users).select_related():
            DonorNotificationEmail(u, self.subject, self.text, self.campaign.pk).send(
                user=u
            )
            time.sleep(1 / settings.EMAIL_MAX_PER_SECOND)

    @hook(AFTER_SAVE, when="draft", is_now=True)
    def on_draft_update(self):
        """
        Send a draft email to the admin who is editing the notification.
        """
        user = self.sent_by
        DonorNotificationEmail(
            user, "DRAFT: " + self.subject, self.text, self.campaign.pk
        ).send(user=user)

    @hook(AFTER_CREATE, when="draft", is_now=False)
    def on_create_publish(self):
        """
        Send real emails to the campaign.
        """
        self.send_notification()

    @hook(AFTER_UPDATE, when="draft", was=True, is_now=False)
    def on_update_publish(self):
        """
        Send real emails to the campaign.
        """
        self.send_notification()
