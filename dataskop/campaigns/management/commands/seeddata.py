# mypy: ignore-errors

from django.contrib.sites.models import Site
from django.core.management.base import BaseCommand
from django.core.management.color import no_style
from django.db import connection, transaction

from dataskop.campaigns.models import Campaign, Donation, Event, SiteExtended
from dataskop.campaigns.tests.factories import (
    DonationFactory,
    EventFactory,
    SiteExtendedFactory,
)
from dataskop.users.models import User
from dataskop.users.tests.factories import UserFactory


class Command(BaseCommand):
    help = "Generate fake data to get started quickly"

    def add_arguments(self, parser):
        parser.add_argument(
            "--delete",
            action="store_true",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        if options["delete"]:
            self.stdout.write("Deleting all old objects (besides superusers)...")

            User.objects.filter(is_superuser=False).delete()
            models = [Campaign, Donation, Site, SiteExtended, Event]
            for m in models:
                self.stdout.write(f"Deleting model `{m}` ...")
                m.objects.all().delete()

            # Reset auto-imcrement to, e.g., ensure that site has pk of 1
            sequence_sql = connection.ops.sequence_reset_sql(no_style(), models)
            with connection.cursor() as cursor:
                for sql in sequence_sql:
                    cursor.execute(sql)

        self.stdout.write("Creating new data...")

        if SiteExtended.objects.count() == 0:
            SiteExtendedFactory(site=Site.objects.first())

        for su in User.objects.filter(is_superuser=True):
            # create new campaign for every superuser
            d1 = DonationFactory(donor=su, unauthorized_email=None)
            for _ in range(10):
                d = DonationFactory(
                    donor=su, unauthorized_email=None, campaign=d1.campaign
                )

            for _ in range(100):
                EventFactory(campaign=d1.campaign)

        for _ in range(10):
            user = UserFactory()
            d = DonationFactory(donor=user, unauthorized_email=None)
            d.donor.delete()

        self.stdout.write(self.style.SUCCESS("done"))
