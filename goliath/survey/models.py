from django.contrib.auth import get_user_model
from django.db import models
from django.urls import reverse
from django.utils.text import slugify
from markupfield.fields import MarkupField
from taggit.managers import TaggableManager

from goliath.casehandling.models import TimeStampMixin

User = get_user_model()


class Survey(TimeStampMixin):
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
    icon_name = models.CharField(
        max_length=255, null=True, blank=True, help_text="Font Awesome Icon Names"
    )
    tags = TaggableManager(blank=True)

    def __str__(self) -> str:
        return self.title

    def save(self, *args, **kwargs):
        self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("survey-new", kwargs={"pk": self.pk, "slug": self.slug})


class SurveyAnswer(TimeStampMixin):
    answers = models.JSONField(null=True)
    survey = models.ForeignKey(
        "Survey", on_delete=models.SET_NULL, null=True, blank=True
    )
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self) -> str:
        return f"#{self.survey} {self.created_at}"
