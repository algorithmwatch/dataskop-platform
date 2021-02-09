from airtable import Airtable
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from tqdm import tqdm

# from ...autocomplete import generate_phrases
from ...models import ExternalSupport


class Command(BaseCommand):
    help = "Import external support from Airtable"

    def handle(self, **kwargs):
        airtable = Airtable(
            settings.AIRTABLE_TABLE, "Goliath", api_key=settings.AIRTABLE_KEY
        )
        entries = airtable.get_all()

        ExternalSupport.objects.all().delete()

        for entry in tqdm(entries):
            fields = entry["fields"]
            tags = fields.pop("tags", [])
            tags = [x.replace("#", "") for x in tags]
            obj = ExternalSupport.objects.create(**fields)
            obj.tags.add(*tags)

        ExternalSupport.objects.sync_search()

        self.stdout.write(
            self.style.SUCCESS(
                "created " + str(len(entries)) + " external support providers"
            )
        )
