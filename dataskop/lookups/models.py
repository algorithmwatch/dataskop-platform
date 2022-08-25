from django.db.models import CharField, TextField
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from model_utils.models import TimeStampedModel


class Lookup(TimeStampedModel):
    """
    Store data (as stringified, compressed JSON) connected to a unique identifier (id).
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

    id = CharField(primary_key=True, max_length=25)
    data = TextField(blank=True, null=True)

    def __str__(self) -> str:
        return self.id + self.data[:5] if self.data else ""
