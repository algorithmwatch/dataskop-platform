# mypy: ignore-errors

from django.contrib.auth import get_user_model
from django.contrib.sites.models import Site
from django.core.management.base import BaseCommand
from django.core.management.color import no_style
from django.db import connection, transaction

from dataskop.campaigns.models import Campaign, Donation, SiteExtended
from dataskop.campaigns.tests.factories import DonationFactory, SiteExtendedFactory

User = get_user_model()


class Command(BaseCommand):
    help = "Generates fake data for donations"

    def add_arguments(self, parser):
        parser.add_argument(
            "--delete",
            action="store_true",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        if options["delete"]:
            self.stdout.write("Deleting old data (besides superusers)...")

            User.objects.filter(is_superuser=False).delete()
            models = [Campaign, Donation, Site, SiteExtended]
            for m in models:
                self.stdout.write(f"Deleting model `{m}` ...")
                m.objects.all().delete()

            # Reset auto-imcrement to, e.g., ensure that site has pk of 1
            sequence_sql = connection.ops.sequence_reset_sql(no_style(), models)
            with connection.cursor() as cursor:
                for sql in sequence_sql:
                    cursor.execute(sql)

        self.stdout.write("Creating new data...")

        SiteExtendedFactory()

        for su in User.objects.filter(is_superuser=True):
            d1 = DonationFactory(donor=su, unauthorized_email=None)
            for _ in range(10):
                DonationFactory(donor=su, unauthorized_email=None, campaign=d1.campaign)

        self.stdout.write(self.style.SUCCESS("done"))
