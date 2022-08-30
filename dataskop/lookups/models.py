from django.contrib.postgres.fields import ArrayField
from django.db import models
from model_utils.models import TimeStampedModel

from dataskop.users.models import User

LOOKUP_ID_LENGTH = 25


class Lookup(models.Model):
    """
    Store binary data connected to a unique identifier (id).
    Generally, we want to store metadata about posts on platforms.

    `id` should be a strings because post ids on platforms vary. Prepend an indentifier
    to make them unique for a platform: yv for youtube video.

    We don't use Postgres' JSONB field for `data` because:
    - we don't do any querying
    - more resource needed (e.g. validation, stored as binary)

    If we will run into problems on scale, we could also reduce the number of rows by
    combining several lookups into one (e.g. group by author) but then a seperate
    index needs to be added to keep the lookup for posts working.
    """

    id = models.CharField(primary_key=True, max_length=LOOKUP_ID_LENGTH)
    data = models.BinaryField()
    job = models.ForeignKey(
        "LookupJob", on_delete=models.SET_NULL, null=True, blank=True
    )

    def __str__(self) -> str:
        return self.id


class LookupJob(TimeStampedModel):
    """
    Manage the process to get lookup data.
    """

    done = models.BooleanField(default=False)
    processing = models.BooleanField(default=False)
    error = models.BooleanField(default=False)
    trusted = models.BooleanField(default=False)
    input_todo = ArrayField(
        models.CharField(max_length=LOOKUP_ID_LENGTH), null=True, blank=True
    )
    input_done = models.JSONField(null=True, blank=True)
    created_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True
    )
    log = models.TextField(default="")

    def __str__(self) -> str:
        return f"{self.pk}  {self.created}"
