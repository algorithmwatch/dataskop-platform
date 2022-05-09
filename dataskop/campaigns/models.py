from datetime import timedelta

from allauth.account.models import EmailAddress
from autoslug import AutoSlugField
from django.contrib.auth import get_user_model
from django.contrib.sites.models import Site
from django.db import models
from django.db.models import Q
from django.urls.base import reverse
from django.utils import timezone
from django_lifecycle import (
    AFTER_CREATE,
    AFTER_SAVE,
    AFTER_UPDATE,
    BEFORE_DELETE,
    LifecycleModelMixin,
    hook,
)
from herald.models import SentNotification
from model_utils import Choices
from model_utils.fields import StatusField
from model_utils.models import TimeStampedModel
from simple_history.models import HistoricalRecords

from dataskop.campaigns.managers import DonationManager
from dataskop.campaigns.notifications import UnauthorizedDonationShouldLoginEmail
from dataskop.utils.email import send_admin_notification

User = get_user_model()


class SiteExtended(models.Model):
    """
    This model adds domain-specific attributes to Django's Site.
    """

    site = models.OneToOneField(Site, on_delete=models.CASCADE)
    support_email = models.EmailField(max_length=255, default="support@example.com")
    from_email = models.EmailField(max_length=255, default="info@example.com")
    https = models.BooleanField(default=True)
    port = models.IntegerField(default=None, blank=True, null=True)

    @property
    def url_origin(self):
        return f"http{'s' if self.https else ''}://{self.site.domain}{self.port if self.port else ''}"

    @property
    def formatted_from(self):
        return f"{self.site.name} <{self.from_email}>"

    def __str__(self):
        return str(self.site)


class Provider(TimeStampedModel):
    """
    A provider is the platform (or website) that gets scraped in combination with a client
    (app/browser extension) that does the work.
    """

    name = models.CharField(
        max_length=255,
        help_text="Platform or website from which the data is scraped, e.g., YouTube",
    )
    client = models.CharField(
        max_length=255,
        default="DataSkop Electron app",
        help_text="Name of the software that collects the data, e.g., DataSkop Electron app",
    )
    scraping_config_schema = models.JSONField(
        null=True,
        blank=True,
        help_text="Optional JSON schema to validate the `scraping_config` of `Campaign`",
    )

    def __str__(self) -> str:
        return f"{self.name} {self.client}"


class StatusOptions(object):
    """
    A hotfix to make status field work with django-simple-history.
    # https://github.com/jazzband/django-simple-history/issues/190#issuecomment-134281202
    """

    STATUS_OPTIONS = Choices("draft", "active", "inactive")


class Campaign(StatusOptions, TimeStampedModel):
    """
    A campaign is an investigation into a specific platform (provider). It has a status
    and is defined in detail by a JSON-based scraping config.
    """

    status = StatusField(choices_name="STATUS_OPTIONS")
    # Optionally disable the creation of new donations.
    accept_new_donations = models.BooleanField(default=True)
    # Featured campaigns get treaten preferably from the client. Right now, the first
    # featured campaign gets chosen automatically and there is no selection for campaings
    # in the Electron app.
    featured = models.BooleanField(default=True)
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
    site = models.ForeignKey(
        Site,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    history = HistoricalRecords(bases=[StatusOptions, TimeStampedModel])

    class Meta:
        permissions = (("assign_campaign", "Assign campaign"),)

    def __str__(self) -> str:
        return self.title


class Donation(LifecycleModelMixin, TimeStampedModel):
    """
    A donation is a crowd-sourced data donation. The donation is connected to a user but
    it can be created without existing user account. So the account gets created with the
    first donation. The donation needs to get verified at some point or the data gets
    removed.

    If a user account for the given email address exists, inform the user that a new
    donation was just made. The user has to verify that the new donation belongs actually
    her/him. The donation can be created without any authentication.
    """

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
    def after_creation_with_unauthorized_email(self):
        """
        On creation, either create a new user account and inform the existing user about
        a new donation.
        """
        assert self.donor is None

        existing_email = EmailAddress.objects.filter(
            email=self.unauthorized_email
        ).first()

        # check if a user exists for the given email address
        if existing_email:
            recenttime = timezone.now() - timedelta(hours=2)
            thefuture = timezone.now() + timedelta(hours=2)

            num_recent_sent = SentNotification.objects.filter(
                user=existing_email.user,
                date_sent__range=(recenttime, thefuture),
                notification_class="dataskop.campaigns.notifications.UnauthorizedDonationShouldLoginEmail",
            ).count()

            # only inform a user if she or he wasn't recently contacted
            if num_recent_sent == 0:
                UnauthorizedDonationShouldLoginEmail(
                    existing_email.user, self.campaign.site
                ).send(user=existing_email.user)
        else:
            assert self.campaign
            assert self.campaign.site
            # create a new account
            User.objects.create_unverified_user_send_mail(
                self.unauthorized_email, self.ip_address, self.campaign.site
            )

    @hook(BEFORE_DELETE)
    def send_admin_notification_before_delete(self):
        """
        Inform admins when a user deletes their account.
        """
        send_admin_notification(
            "Donation Deleted",
            f"Donation with id {self.pk}, for campaign {self.campaign}, was deleted",
        )


class Event(TimeStampedModel):
    """
    A event for basic analytics that has a message and an optional JSON-based data field.
    """

    campaign = models.ForeignKey(
        "Campaign", on_delete=models.SET_NULL, null=True, blank=True
    )
    message = models.CharField(max_length=100, null=True, blank=True)
    data = models.JSONField(null=True, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)

    def __str__(self) -> str:
        return f"{self.created} / {self.message} / {self.ip_address}"


class DonorNotificationSetting(TimeStampedModel):
    """
    Users can opt-out of notifications for their donations.
    """

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
    )
    disable_all = models.BooleanField(default=False)
    # user's can manually opt-out of notifications for a specific campaign
    disabled_campaigns = models.ManyToManyField("Campaign", blank=True)


class DonorNotification(LifecycleModelMixin, TimeStampedModel):
    """
    Send a notification (email) to all donors of a campaign.
    """

    # NB: `sent_by` and `campaign` can't be blank in the admin form
    sent_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=False)
    draft = models.BooleanField(
        default=True,
        help_text="If you set draft to false, the email will get sent to the chosen \
campaign (and can't be changed anymore).",
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
        """
        Send notifcation to all donors of the campaign.
        """
        assert self.campaign is not None

        users = User.objects.filter(
            pk__in=(
                self.campaign.donation_set.confirmed().values_list("donor").distinct()
            )
        )

        exclude_users = DonorNotificationSetting.objects.filter(
            Q(disable_all=True) | Q(disabled_campaigns=self.campaign)
        ).values_list("user")

        from dataskop.campaigns.tasks import send_donor_notification_email

        for user in users.exclude(pk__in=exclude_users).select_related():
            send_donor_notification_email.delay(
                user.pk,
                self.subject,
                self.text,
                self.campaign.pk,
            )

    @hook(AFTER_SAVE, when="draft", is_now=True)
    def on_draft_update(self):
        """
        Send a draft email to the admin who is editing the notification.

        Send the email through celery because we want to check if the celery process has
        the latest code changes. We had problems in the past, that the celery worker was
        out of sync.
        """
        assert self.campaign is not None

        from dataskop.campaigns.tasks import send_donor_notification_email

        user = self.sent_by
        send_donor_notification_email.delay(
            user.pk,
            f"DRAFT: {self.subject}",
            self.text,
            self.campaign.pk,
        )

    @hook(AFTER_CREATE, when="draft", is_now=False)
    def on_create_publish(self):
        """
        Send real emails to the campaign on creation when `draft` is false.
        """
        self.send_notification()

    @hook(AFTER_UPDATE, when="draft", was=True, is_now=False)
    def on_update_publish(self):
        """
        Send real emails to the campaign on setting `draft` to false.
        """
        self.send_notification()
