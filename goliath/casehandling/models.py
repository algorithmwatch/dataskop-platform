import datetime

import cleantext
from allauth.account.models import EmailAddress
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.postgres.fields import ArrayField
from django.contrib.postgres.indexes import GinIndex
from django.contrib.postgres.search import SearchVectorField
from django.contrib.sites.models import Site
from django.db import models
from django.template import Context, Template
from django.urls import reverse
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _
from markupfield.fields import MarkupField
from simple_history.models import HistoricalRecords
from taggit.managers import TaggableManager

from .managers import CaseManager
from .search import SearchCaseTypeQuerySet, SearchExpertnalSupportQuerySet

User = get_user_model()


class TimeStampMixin(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Entity(TimeStampMixin):
    """Generic complaint / request recipient"""

    name = models.CharField(max_length=255)
    description = MarkupField(
        markup_type="markdown", blank=True, null=True, help_text="Markdown is available"
    )
    email = models.EmailField()
    url = models.URLField(blank=True, null=True)

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
    title = models.CharField(max_length=50)
    slug = models.SlugField(
        default="", editable=False, max_length=255, null=False, blank=False
    )
    claim = models.CharField(max_length=100, null=True, blank=True)
    short_description = models.CharField(max_length=500, null=True, blank=True)
    description = MarkupField(
        markup_type="markdown", blank=True, null=True, help_text="Markdown is available"
    )
    questions = models.JSONField(
        help_text="""Please go to https://surveyjs.io/create-survey and paste the JSON 'JSON Editor'.
        Then go to 'Survey Designer' to edit the survey.Try it out with 'Test Survey'.
        When you are done, paste the JSON in this field and hit save."""
    )
    entities = models.ManyToManyField("Entity", blank=True)
    needs_approval = models.BooleanField(default=False)
    autoreply_keywords = models.ManyToManyField("AutoreplyKeyword", blank=True)
    order = models.FloatField(
        null=True,
        blank=True,
        help_text="If not null, show this casetype on the front page. In order of this value.",
    )
    icon_name = models.CharField(
        max_length=255, null=True, blank=True, help_text="Font Awesome Icon Names"
    )
    tags = TaggableManager(blank=True)

    # TODO: various email / message strings must not be `null=True` but could not remove them without writing a seperate migration.

    # what the user can answer to the entity
    auto_reply_subject = models.CharField(
        max_length=255,
        default="Bitte um Antwort ",
        null=True,
        help_text="user reply subject to the entity",
    )
    auto_reply_text = models.TextField(
        default="""herzlichen Dank für Ihre Mail. Leider beantwortet diese meine Frage nicht. Bisherige Versuche, das Problem über andere Formulare, FAQs oder Hilfe-Foren zu lösen, haben leider nicht zum Erfolg geführt.

Ich möchte Sie daher bitten, mir eine*n direkte*n Ansprechpartner*in zu vermitteln.
""",
        null=True,
        help_text="user reply text to the entity",
    )

    # email settings
    letter_subject_custom_template = models.TextField(
        null=True,
        blank=True,
        help_text="subject (django template) initial email sent to the entities",
    )
    letter_template = models.TextField(
        null=True,
        blank=True,
        help_text="context/body/text (django template) initial email sent to the entities",
    )

    user_notification_new_answer_custom_text = models.TextField(
        null=True,
        default="auf Ihre Fallmeldung erhalten. Schau Sie nach, ob sich Ihr Anliegen damit gelöst hat oder ob Sie weitere Schritte einleiten wollen.",
        help_text="special text for the noficiation email if the entity answered",
    )
    user_notification_reminder_custom_text = models.TextField(
        null=True,
        default="auf Ihre Fallmeldung erhalten, die Sie jetzt bewerten können. Lassen Sie uns wissen, wie zufrieden Sie mit der Reaktion sind.",
        help_text="special text for the reminder email if the user has to choose a status",
    )

    # send to entity
    entity_notification_reminder_custom_text = models.TextField(
        null=True,
        default="Bisher habe ich leider keine Antwort erhalten. Ich freue mich über eine zeitnahe Rückmeldung.",
        help_text="special text for the entity notification email",
    )
    user_notification_entity_notification_reminder_custom_text = models.TextField(
        null=True,
        default="daran erinnert, dass Sie bisher noch keine Antwort auf ihre Fallmeldung erhalten haben. Bei neuen Entwicklungen benachrichtigen wir Sie per E-Mail.",
        help_text="What note should users receive when the entity is reminded to respond?",
    )

    # reminder settings
    user_reminder_max = models.IntegerField(
        default=2, help_text="Remind X times and then stop"
    )
    user_reminder_margin = models.DurationField(
        default=datetime.timedelta(days=7),
        help_text="Format: DAYS HOURS:MINUTES:SECONDS e.g. for 7 days: `7 00:00:00`, for every minute `00:01:00`",
    )
    entity_reminder_max = models.IntegerField(
        default=2, help_text="Remind X times and then stop"
    )
    entity_reminder_margin = models.DurationField(
        default=datetime.timedelta(days=7),
        help_text="Format: DAYS HOURS:MINUTES:SECONDS e.g. for 7 days: `7 00:00:00`, for every minute `00:01:00`",
    )

    history = HistoricalRecords(
        excluded_fields=[
            "_description_rendered",
            "description_markup_type",
            "search_vector",
        ]
    )

    # NB: no search index used now, if needed: at a new Gin Index
    search_vector = SearchVectorField(null=True, blank=True)
    search = SearchCaseTypeQuerySet.as_manager()
    objects = models.Manager()

    def save(self, *args, **kwargs):
        self.slug = slugify(self.title)
        super().save(*args, **kwargs)

        # Sync all case types after each save. Not neccesary, should be changed to only update `search_vector`
        #  of an object.
        CaseType.search.sync_search()

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("new-wizzard", kwargs={"pk": self.pk, "slug": self.slug})

    def is_message_autoreply(self, message):
        for keyword in self.autoreply_keywords.all():
            if keyword.text_caseinsensitiv.lower() in message.lower():
                return True
        return False

    def render_letter_subject(self, case):
        if self.letter_subject_custom_template:
            subject_text = Template(self.letter_subject_custom_template).render(
                Context(self)
            )
            return (
                cleantext.normalize_whitespace(subject_text, no_line_breaks=True)
                + f" #{case.id}"
            )
        else:
            return f'Neuer Fall von "{self.title}" auf Unding.de #{case.id}'

    def render_letter(self, answers: dict, username: str):
        tpl_letter = Template(self.letter_template)

        if answers is None or type(answers) is str:
            return ""

        answers["username"] = username
        text = str(tpl_letter.render(Context(answers)))
        text = cleantext.normalize_whitespace(
            text,
            strip_lines=True,
            no_line_breaks=False,
            keep_two_line_breaks=True,
        )
        return text


class Case(TimeStampMixin):
    class Status(models.TextChoices):
        WAITING_EMAIL_ERROR = "EE", "Fehler beim E-Mail-Versandt"
        WAITING_USER_VERIFIED = "UV", "Warten auf User-Verifizierung"
        WAITING_CASE_APPROVED = "CA", "Warte auf Admin-Approval"
        WAITING_INITIAL_EMAIL_SENT = "ES", "E-Mail wird versendet"
        WAITING_RESPONSE = "WR", "Warten auf Antwort"
        WAITING_USER_INPUT = "WU", "Handlung erforderlich"
        CLOSED_NEGATIVE = "CN", "Abgeschlossen"
        CLOSED_POSITIVE = "CP", "Abgeschlossen"
        CLOSED_MIXED = "CM", "Abgeschlossen"

    slug = models.SlugField(
        default="", editable=False, max_length=255, null=False, blank=False
    )
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
    answers_subject = models.CharField(max_length=255, null=True, blank=True)
    answers_text = models.TextField(null=True, blank=True)
    approved_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="approved_cases",
    )
    sent_user_reminders = models.IntegerField(default=0)
    last_user_reminder_sent_at = models.DateTimeField(null=True, blank=True)
    sent_entities_reminders = models.IntegerField(default=0)
    last_entities_reminder_sent_at = models.DateTimeField(null=True, blank=True)
    post_cc = models.ForeignKey(
        "PostCaseCreation",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="cases",
    )

    history = HistoricalRecords()
    objects = CaseManager()

    def __str__(self) -> str:
        return f"#{self.pk} {self.case_type}"

    def save(self, *args, **kwargs):
        # `case_type` may be `None` in e.g. a testing environment

        # add a dummy slug `nocasetype` if there is no case type to make routing work
        if self.slug is None or self.slug == "":
            self.slug = (
                "nocasetype"
                if self.case_type is None
                else slugify(self.case_type.title)
            )
        elif self.slug == "nocasetype" and self.case_type is not None:
            self.slug = slugify(self.case_type.title)

        # render the letter text only if there is a case type
        if self.answers_text is None and self.case_type is not None:
            self.answers_text = self.case_type.render_letter(
                self.answers, self.user.full_name
            )

        super().save(*args, **kwargs)

        # render the subject after creating the object because we need the pk / id for the subject
        if self.answers_subject is None and self.case_type is not None:
            self.answers_subject = self.case_type.render_letter_subject(self)
            self.save()

    def get_absolute_url(self):
        return reverse("cases-detail", kwargs={"pk": self.pk, "slug": self.slug})

    @property
    def print_status(self):
        if self.status in (
            self.Status.WAITING_USER_INPUT,
            self.Status.WAITING_USER_VERIFIED,
        ):
            return "0_open"
        if self.status in (
            self.Status.CLOSED_NEGATIVE,
            self.Status.CLOSED_POSITIVE,
            self.Status.CLOSED_MIXED,
        ):
            return "2_closed"
        return "1_waiting"

    @property
    def all_messages(self):
        return sorted(
            list(self.receivedmessage_set.all()) + list(self.sentmessage_set.all()),
            key=lambda x: x.sent_at,
        )

    @property
    def is_approved(self):
        return not self.case_type.needs_approval or self.approved_by is not None

    @property
    def is_user_verified(self):
        return EmailAddress.objects.filter(user=self.user, verified=True).exists()

    @property
    def is_sane(self):
        return self.is_user_verified and self.is_approved

    def handle_incoming_email(self, is_autoreply):
        if is_autoreply:
            pass
        else:
            from .tasks import send_user_notification_new_message

            # FIXME: selected entites may have more items
            text = f"""Sie haben eine Antwort von {self.selected_entities.first().name} {self.case_type.user_notification_new_answer_custom_text}"""

            send_user_notification_new_message(
                self.user.email,
                settings.URL_ORIGIN + self.get_absolute_url(),
                text,
                f"Neue Antwort #{self.pk}",
                self.user.full_name,
            )
            self.status = self.Status.WAITING_USER_INPUT
            self.save()

    @property
    def last_action_at(self):
        last_action_date = None
        if self.history.all().count() == 0:
            # there is no history, the object was never updated since creation
            last_action_date = self.created_at
        else:
            # getting the most recent version (in the history)
            prev_case = self.history.first()
            while True:
                if prev_case is None:
                    # there is no history
                    break
                if prev_case.status == self.status:
                    # no status changed, go further back
                    last_action_date = prev_case.history_date
                    break
                # iterate through the all the history item
                prev_case = prev_case.prev_record
        return last_action_date

    def send_user_reminder(self):
        from .tasks import send_user_notification_reminder

        # FIXME: selected entites may have more items
        text = f"""Sie haben eine Antwort von {self.selected_entities.first().name} {self.case_type.user_notification_reminder_custom_text}"""

        send_user_notification_reminder(
            self.user.email,
            settings.URL_ORIGIN + self.get_absolute_url(),
            text,
            "Bitte setzen Sie den Status #" + str(self.pk),
            self.user.full_name,
        )
        self.last_user_reminder_sent_at = datetime.datetime.now()
        self.sent_user_reminders += 1
        self.save()

    def send_entities_reminder(self):
        from .tasks import (
            send_entity_message,
            send_user_notification_reminder_to_entity,
        )

        site = Site.objects.get_current()
        site_short = f"{site.name} ({site.domain})"

        for e in self.selected_entities.all():
            text = f"""Guten Tag {e.name},

am {self.created_at.strftime("%d.%m.%Y um %H:%M Uhr")} habe ich Ihnen eine Anfrage mit dem Botendienst von {site_short} zukommen lassen. {self.case_type.entity_notification_reminder_custom_text}

Mit freundlichen Grüßen
{self.user.full_name}"""

            send_entity_message(
                e.email,
                self,
                text,
                "Bitte Antworten Sie auf unsere Anfrage #" + str(self.pk),
            )

        self.last_entities_reminder_sent_at = datetime.datetime.now()
        # can't use F expression because django-simple-history does not support it
        self.sent_entities_reminders += 1
        self.save()

        entity_names = " ,".join([x.name for x in self.selected_entities.all()])
        notify_text = f"""wir haben für Sie {entity_names} {self.case_type.user_notification_entity_notification_reminder_custom_text}

Den aktuellen Status Ihres Falles können Sie hier einsehen:
"""

        send_user_notification_reminder_to_entity(
            self.user.email,
            settings.URL_ORIGIN + self.get_absolute_url(),
            notify_text,
            "Erinnerung verschickt #" + str(self.pk),
            self.user.full_name,
        )

    def send_auto_reply_message_to_entity(self):
        from .tasks import send_entity_message

        for e in self.selected_entities.all():

            text = f"""Guten Tag {e.name},

{self.case_type.auto_reply_text}

Mit freundlichen Grüßen
{self.user.full_name}"""

            send_entity_message(
                self.email,
                self,
                text,
                self.case_type.auto_reply_subject + f"#{self.pk}",
            )

    def construct_answer_thread(self):
        """
        https://stackoverflow.com/questions/5420402/reliable-way-to-only-get-the-email-text-excluding-previous-emails
        """
        result_text = ""
        quote_level = 0

        for m in reversed(self.all_messages):
            intro = "Am " + m.sent_at.strftime("%d.%m.%Y, %H:%M") + " schrieb "
            if isinstance(m, ReceivedMessage):
                intro += m.from_display_name + " <" + m.from_display_email
            else:
                intro += self.user.full_name + " <" + self.email

            intro += "> folgendes:\n"
            if quote_level > 0:
                intro = (">" * quote_level) + " " + intro
            text = intro

            # important: only increment here to keep the intro one quote level below
            quote_level += 1

            new_content = (
                m.parsed_content if isinstance(m, ReceivedMessage) else m.last_content
            )
            lines = new_content.splitlines() + ["\n"]
            lines = [(">" * quote_level) + " " + x for x in lines]
            text += "\n".join(lines)
            result_text += text.rstrip() + "\n"

        return result_text

    # FIXME: ???
    def sent_message_to_entity(self):
        pass


class PostCaseCreation(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    case_type = models.ForeignKey(
        "CaseType", on_delete=models.SET_NULL, null=True, blank=True
    )
    is_contactable = models.BooleanField(_("Kontaktierbar"), default=False)
    post_creation_hint = models.TextField(_("Hinweis"), null=True, blank=True)
    sent_initial_emails_at = models.DateTimeField(null=True, blank=True)

    def get_absolute_url(self):
        return reverse("post-wizzard-success", kwargs={"pk": self.pk})

    def send_all_initial_emails(self):
        from .tasks import send_initial_emails_to_entities

        send_initial_emails_to_entities(self)

    def user_verified_afterwards(self):
        """
        change status and thus trigger email sending (see tasks.py)
        """
        # if the emails were already sent, don't do anything

        send_emails = False
        for case in self.cases.all():
            if len(case.all_messages) > 0:
                return

            if case.is_approved:
                case.status = case.Status.WAITING_INITIAL_EMAIL_SENT
                send_emails = True
            else:
                case.status = case.Status.WAITING_CASE_APPROVED
            case.save()

        if send_emails:
            self.send_all_initial_emails()

    def approve_case(self, user):
        """
        change status and thus trigger email sending (see tasks.py)
        """

        send_emails = False
        for case in self.cases.all():
            # if the emails were already sent, don't do anything
            if len(case.all_messages) > 0:
                return

            case.approved_by = user
            if case.is_user_verified:
                case.status = case.Status.WAITING_INITIAL_EMAIL_SENT
                send_emails = True
            else:
                case.status = case.Status.WAITING_USER_VERIFIED
            case.save()

        if send_emails:
            self.send_all_initial_emails()


class Message(TimeStampMixin):
    from_email = models.EmailField()
    # can be null to store emails that belong to no case (not sure what to do with those)
    to_email = models.EmailField(null=True, blank=True)
    subject = models.CharField(max_length=255)
    content = models.TextField()
    case = models.ForeignKey("Case", on_delete=models.SET_NULL, null=True, blank=True)
    sent_at = models.DateTimeField()

    class Meta:
        abstract = True
        ordering = ["sent_at"]

    def __str__(self):
        return self.subject + self.from_email + self.to_email if self.to_email else ""


class SentMessage(Message):
    last_content = models.TextField()  # only the last part without the whole thread
    esp_message_id = models.CharField(max_length=255, null=True)
    esp_message_status = models.CharField(max_length=255, null=True)
    error_message = models.TextField(blank=True, null=True)
    history = HistoricalRecords()

    @property
    def is_reply(self):
        return False


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

    @property
    def is_reply(self):
        return True


class ReceivedAttachment(models.Model):
    file = models.FileField(upload_to="private_attachments")
    filename = models.TextField(blank=True, null=True)
    content_type = models.TextField(blank=True, null=True)
    content_disposition = models.CharField(blank=True, null=True, max_length=20)
    message = models.ForeignKey(
        "ReceivedMessage", on_delete=models.SET_NULL, null=True, blank=True
    )

    def get_absolute_url(self):
        return self.file.url

    def __str__(self):
        return self.file.url


# FIXME: currently not used
class UserReplyChoice(models.Model):
    subject = models.CharField(max_length=255)
    content = models.TextField()


class ExternalSupport(TimeStampMixin):
    name = models.CharField(max_length=255, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    url = models.CharField(max_length=255, blank=True, null=True)
    tags = TaggableManager(blank=True)
    search_vector = SearchVectorField(null=True, blank=True)
    objects = models.Manager()
    search = SearchExpertnalSupportQuerySet.as_manager()

    class Meta(object):
        indexes = [GinIndex(fields=["search_vector"])]


# TODO: put into seperate app
from django.contrib.flatpages.models import FlatPage


class GoliathFlatPage(FlatPage):
    social_media_image = models.ForeignKey(
        "PublicFile", on_delete=models.SET_NULL, null=True, blank=True
    )
    social_media_description = models.TextField(blank=True, null=True)
    markdown_content = MarkupField(markup_type="markdown", blank=True, null=True)

    history = HistoricalRecords(
        excluded_fields=["_markdown_content_rendered", "markdown_content_markup_type"]
    )


class PublicFile(models.Model):
    file = models.FileField(upload_to="public_files")

    def get_absolute_url(self):
        return self.file.url

    def __str__(self):
        return self.file.url
