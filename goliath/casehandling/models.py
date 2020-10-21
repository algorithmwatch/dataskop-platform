from django.contrib.postgres.fields import JSONField
from django.db import models
from goliath.users.models import User


class TimeStampMixin(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Status(models.TextChoices):
    WAITING_RESPONSE = "WR", "Waiting for response"
    WAITING_USER = "WU", "Waiting for user input"
    CLOSED_NEGATIVE = "CN", "Closed, given up"
    CLOSED_POSITIVE = "CP", "Closed, case resolved"
    CLOSED_MIXED = "CM", "Closed, mixed feelings"


class Entity(TimeStampMixin):
    """Generic complaint / request recipient"""

    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    email = models.EmailField()
    url = models.URLField(blank=True, null=True)

    def __str__(self):
        return self.name


class CaseType(TimeStampMixin):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    questions = JSONField()
    entity = models.ForeignKey("Entity", on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return self.name + " " + str(self.entity)


class Case(TimeStampMixin):
    questions = JSONField(null=True)
    answers = JSONField(null=True)
    email = models.EmailField()
    status = models.CharField(
        max_length=2,
        choices=Status.choices,
        default=Status.WAITING_RESPONSE,
    )
    case_type = models.ForeignKey("CaseType", on_delete=models.SET_NULL, null=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    entity = models.ForeignKey("Entity", on_delete=models.SET_NULL, null=True)

    # not getting called right now
    # def save(self, *args, **kwargs):
    #     if self.email is None:
    #         self.email = self.user.name + random_string(4) + "@aw.jfilter.de"
    #     super(Case, self).save(*args, **kwargs)

    def get_absolute_url(self):
        return f"/case/{self.pk}/"


class Message(TimeStampMixin):
    from_email = models.EmailField()
    to_email = models.EmailField()
    subject = models.CharField(max_length=255)
    content = models.TextField()
    case = models.ForeignKey("Case", on_delete=models.SET_NULL, null=True)
    sent_at = models.DateTimeField()

    class Meta:
        abstract = True
        ordering = ["-sent_at"]

    def __str__(self):
        return self.from_email + self.to_email + self.subject


class SentMessage(Message):
    esp_message_id = models.CharField(max_length=255, null=True)
    esp_message_status = models.CharField(max_length=255, null=True)
    error_message = models.TextField(blank=True, null=True)


class ReceivedMessage(Message):
    received_at = models.DateTimeField()
    html = models.TextField(blank=True, null=True)
