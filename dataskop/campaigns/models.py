from autoslug import AutoSlugField
from django.contrib.auth import get_user_model
from django.db import models
from django_lifecycle import AFTER_CREATE, LifecycleModel, hook
from model_utils import Choices
from model_utils.fields import StatusField
from model_utils.models import StatusModel, TimeStampedModel
from simple_history.models import HistoricalRecords

User = get_user_model()

# https://github.com/jazzband/django-simple-history/issues/190#issuecomment-134281202
class StatusOptions(object):
    STATUS_OPTIONS = Choices("draft", "active", "inactive")


class Campaign(StatusOptions, TimeStampedModel):
    status = StatusField(choices_name="STATUS_OPTIONS")
    title = models.CharField(max_length=255)
    slug = AutoSlugField(populate_from="title")
    description = models.TextField(null=True, blank=True)
    created_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True
    )
    scraper_config = models.JSONField(null=True, blank=True)
    history = HistoricalRecords(bases=[StatusOptions, TimeStampedModel])

    class Meta:
        permissions = (("assign_campaign", "Assign campaign"),)

    def __str__(self) -> str:
        return self.title


class Donation(LifecycleModel, TimeStampedModel):
    campaign = models.ForeignKey(
        "Campaign", on_delete=models.SET_NULL, null=True, blank=True
    )
    donor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    results = models.JSONField(null=True, blank=True)
    unauthorized_email = models.EmailField(null=True, blank=True)

    def __str__(self) -> str:
        return f"{self.campaign} / {self.created} / {self.donor} / {self.unauthorized_email}"

    @hook(AFTER_CREATE, when="unauthorized_email", is_not=None)
    def after_creattion_with_unauthorized_email(self):
        User.objects.create_unverified_user_send_mail(self.unauthorized_email)
