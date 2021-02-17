import datetime

import cleantext
from allauth.account.models import EmailAddress
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.postgres.fields import ArrayField
from django.contrib.postgres.indexes import GinIndex
from django.contrib.postgres.search import (
    SearchHeadline,
    SearchQuery,
    SearchRank,
    SearchVector,
    SearchVectorField,
)
from django.db import models
from django.db.models import F
from django.template import Context, Template
from django.urls import reverse
from markupfield.fields import MarkupField
from simple_history.models import HistoricalRecords
from taggit.managers import TaggableManager

from ..utils.time import date_within_margin

User = get_user_model()


class SearchExpertnalSupportQuerySet(models.QuerySet):
    def search(self, search_text, highlight=True):
        if search_text is None:
            return self

        search_query = SearchQuery(
            search_text, config="german", search_type="websearch"
        )

        qs = self.filter(search_vector=search_query)
        qs = qs.annotate(rank=SearchRank(F("search_vector"), search_query)).order_by(
            "-rank"
        )

        if highlight:
            qs = qs.annotate(
                name_highlighted=SearchHeadline(
                    "name", search_query, config="german", highlight_all=True
                ),
                description_highlighted=SearchHeadline(
                    "description", search_query, config="german", highlight_all=True
                ),
            )

        return qs

    def sync_search(self):
        self.update(
            search_vector=SearchVector("name", weight="A", config="german")
            + SearchVector("description", weight="B", config="german")
        )


class TimeStampMixin(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Status(models.TextChoices):
    WAITING_EMAIL_ERROR = "EE", "There was error with sending the email"
    WAITING_USER_VERIFIED = "UV", "Waiting user verification"
    WAITING_CASE_APPROVED = "CA", "Waiting admin approval"
    WAITING_INITIAL_EMAIL_SENT = "ES", "Waiting until initial email sent"
    WAITING_RESPONSE = "WR", "Waiting for response"
    WAITING_USER_INPUT = "WU", "Waiting for user input"
    CLOSED_NEGATIVE = "CN", "Closed, given up"
    CLOSED_POSITIVE = "CP", "Closed, case resolved"
    CLOSED_MIXED = "CM", "Closed, mixed feelings"


class Entity(TimeStampMixin):
    """Generic complaint / request recipient"""

    name = models.CharField(max_length=255)
    description = MarkupField(default_markup_type="markdown", blank=True, null=True)
    email = models.EmailField()
    url = models.URLField(blank=True, null=True)

    # remove those two fieds to make it work, FIXME: a least make `description_markup_type` work again
    history = HistoricalRecords(
        excluded_fields=["_description_rendered", "description_markup_type"]
    )

    def __str__(self):
        return self.name


class AutoreplyKeyword(models.Model):
    text_caseinsensitiv = models.TextField()

    def __str__(self):
        return str(self.text_caseinsensitiv)


class CaseType(TimeStampMixin):
    name = models.CharField(max_length=255)
    description = MarkupField(default_markup_type="markdown", blank=True, null=True)
    questions = models.JSONField(
        help_text="Please go to https://surveyjs.io/create-survey and paste the JSON 'JSON Editor'. Then go to 'Survey Designer' to edit the survey. Try it out with 'Test Survey'. When you are done, paste the JSON in this field and hit save."
    )
    entities = models.ManyToManyField("Entity", blank=True)
    needs_approval = models.BooleanField(default=False)
    autoreply_keywords = models.ManyToManyField("AutoreplyKeyword", blank=True)
    order = models.FloatField(null=True, blank=True)
    icon_name = models.CharField(max_length=255)
    letter_template = models.TextField(null=True, blank=True)
    tags = TaggableManager()

    # remove those two fieds to make it work, FIXME: a least make `description_markup_type` work again
    history = HistoricalRecords(
        excluded_fields=["_description_rendered", "description_markup_type"]
    )

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("new-wizzard", args=(self.pk,))

    def is_message_autoreply(self, message):
        for keyword in self.autoreply_keywords.all():
            if keyword.text_caseinsensitiv.lower() in message.lower():
                return True
        return False

    def render_letter(self, answers: dict, username: str):
        tpl = Template(self.letter_template)
        answers["username"] = username
        text = str(tpl.render(Context(answers))).strip()
        text = cleantext.normalize_whitespace(
            text,
            strip_lines=True,
            no_line_breaks=False,
            keep_two_line_breaks=True,
        )
        return text


class CaseManager(models.Manager):
    def remind_users(
        self,
        margin: datetime.timedelta = datetime.timedelta(days=7),
        max_reminders: int = 2,
    ):
        """
        Iterate over all user and check if they should get a reminder.
        Default: remind after 7 days, then remind again after 7 days and stop.
        """

        def _get_last_action_date(case):
            last_action_date = None
            if case.history.all().count() == 0:
                # there is no history, the object was never updated since creation
                last_action_date = case.created_at
            else:
                # getting the most recent version (in the history)
                prev_case = case.history.first()
                while True:
                    if prev_case is None:
                        # there is no history
                        break
                    if prev_case.status == case.status:
                        # no status changed, go further back
                        last_action_date = prev_case.history_date
                        break
                    # iterate through the all the history item
                    prev_case = prev_case.prev_record
            return last_action_date

        emails_sent = 0
        for case in self.filter(
            status=Status.WAITING_USER_INPUT, sent_reminders__lt=max_reminders
        ):
            if case.last_reminder_sent_at is not None and date_within_margin(
                case.last_reminder_sent_at, margin
            ):
                continue

            last_action_date = _get_last_action_date(case)
            if last_action_date is not None:
                # there was a status change
                if not date_within_margin(last_action_date, margin):
                    # and there was no status update for at least $margin time
                    case.send_reminder()
                    emails_sent += 1
        return emails_sent


class Case(TimeStampMixin):
    questions = models.JSONField(null=True)
    answers = models.JSONField(null=True)
    email = models.EmailField(unique=True)
    status = models.CharField(
        max_length=2,
        choices=Status.choices,
    )
    case_type = models.ForeignKey(
        "CaseType", on_delete=models.SET_NULL, null=True, blank=True
    )
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    selected_entities = models.ManyToManyField("Entity", blank=True)
    answers_text = models.TextField(null=True, blank=True)
    approved_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="approved_cases",
    )
    sent_reminders = models.IntegerField(default=0)
    last_reminder_sent_at = models.DateTimeField(null=True, blank=True)

    history = HistoricalRecords()
    objects = CaseManager()

    @property
    def print_status(self):
        if self.status in (
            Status.WAITING_USER_INPUT,
            Status.WAITING_USER_VERIFIED,
        ):
            return "0_open"
        if self.status in (
            Status.CLOSED_NEGATIVE,
            Status.CLOSED_POSITIVE,
            Status.CLOSED_MIXED,
        ):
            return "2_closed"
        return "1_waiting"

    def get_absolute_url(self):
        return reverse("cases-detail", args=(self.pk,))

    def all_messages(self):
        return sorted(
            list(self.receivedmessage_set.all()) + list(self.sentmessage_set.all()),
            key=lambda x: x.sent_at,
        )

    def is_approved(self):
        return not self.case_type.needs_approval or self.approved_by is not None

    def is_user_verified(self):
        return EmailAddress.objects.filter(user=self.user, verified=True).exists()

    def is_sane(self):
        return self.is_user_verified() and self.is_approved()

    def user_verified_afterwards(self):
        """
        change status and thus trigger email sending (see tasks.py)
        """
        if self.is_approved():
            self.status = Status.WAITING_INITIAL_EMAIL_SENT
            # avoid circular imports
            from .tasks import send_initial_emails

            send_initial_emails(self)
        else:
            self.status = Status.WAITING_CASE_APPROVED
        self.save()

    def approve_case(self, user):
        """
        change status and thus trigger email sending (see tasks.py)
        """
        self.approved_by = user
        if self.is_user_verified():
            self.status = Status.WAITING_INITIAL_EMAIL_SENT
            # avoid circular imports
            from .tasks import send_initial_emails

            send_initial_emails(self)
        else:
            self.status = Status.WAITING_USER_VERIFIED
        self.save()

    def handle_incoming_email(self, is_autoreply):
        if is_autoreply:
            pass
        else:
            from .tasks import send_new_message_notification

            send_new_message_notification(
                self.user.email, settings.URL_ORIGIN + self.get_absolute_url()
            )
            self.status = Status.WAITING_USER_INPUT
            self.save()

    def send_reminder(self):
        from .tasks import send_reminder_notification

        send_reminder_notification(
            self.user.email, settings.URL_ORIGIN + self.get_absolute_url()
        )
        self.last_reminder_sent_at = datetime.datetime.now()
        self.sent_reminders += 1
        self.save()


class Message(TimeStampMixin):
    from_email = models.EmailField()
    to_email = models.EmailField()
    subject = models.CharField(max_length=255)
    content = models.TextField()
    case = models.ForeignKey("Case", on_delete=models.SET_NULL, null=True, blank=True)
    sent_at = models.DateTimeField()

    class Meta:
        abstract = True
        ordering = ["sent_at"]

    def __str__(self):
        return self.from_email + self.to_email + self.subject


class SentMessage(Message):
    esp_message_id = models.CharField(max_length=255, null=True)
    esp_message_status = models.CharField(max_length=255, null=True)
    error_message = models.TextField(blank=True, null=True)
    history = HistoricalRecords()


class ReceivedMessage(Message):
    received_at = models.DateTimeField()
    html = models.TextField(blank=True, null=True)
    from_display_name = models.TextField(null=True, blank=True)
    from_display_email = models.EmailField()
    spam_score = models.FloatField()
    to_addresses = ArrayField(models.TextField())
    cc_addresses = ArrayField(models.TextField(), null=True, blank=True)
    is_autoreply = models.BooleanField(null=True)
    parsed_content = models.TextField()
    history = HistoricalRecords()


class ExternalSupport(TimeStampMixin):
    name = models.CharField(max_length=255, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    url = models.CharField(max_length=255, blank=True, null=True)
    tags = TaggableManager()
    search_vector = SearchVectorField(null=True)

    objects = SearchExpertnalSupportQuerySet.as_manager()

    class Meta(object):
        indexes = [GinIndex(fields=["search_vector"])]


# TODO: put into seperate app
from django.contrib.flatpages.models import FlatPage


class GoliathFlatPage(FlatPage):
    markdown_content = MarkupField(
        default_markup_type="markdown", blank=True, null=True
    )
