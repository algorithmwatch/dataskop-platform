from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import transaction
from django.db.models import signals

from dataskop.campaigns.models import Campaign, Donation
from dataskop.campaigns.tests.factories import DonationFactory

User = get_user_model()


class Command(BaseCommand):
    help = "Generates fake data for donations"

    def add_arguments(self, parser):
        parser.add_argument(
            "--delete",
            action="store_true",
        )

    # mute signals when creating fake data (via https://stackoverflow.com/a/26490827/4028896)

    # @factory.django.mute_signals(signals.pre_save, signals.post_save)
    @transaction.atomic
    def handle(self, *args, **options):

        if options["delete"]:
            self.stdout.write("Deleting old data (besides superusers)...")

            User.objects.filter(is_superuser=False).delete()
            models = [Campaign, Donation]
            for m in models:
                m.objects.all().delete()

        self.stdout.write("Creating new data...")

        for su in User.objects.filter(is_superuser=True):
            d1 = DonationFactory(donor=su, unauthorized_email=None)
            for _ in range(10):
                DonationFactory(donor=su, unauthorized_email=None, campaign=d1.campaign)

        self.stdout.write(self.style.SUCCESS("done"))
