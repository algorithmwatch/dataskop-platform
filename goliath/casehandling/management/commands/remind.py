import datetime

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from ...models import Case


class Command(BaseCommand):
    help = "remind people to update their status"

    def add_arguments(self, parser):
        parser.add_argument(
            "--minutes",
            type=int,
        )

    def handle(self, **kwargs):
        self.stdout.write("check for people who need a reminder")
        if kwargs["minutes"]:
            self.stdout.write("using provided minutes over the default")
            emails_sent = Case.objects.remind_users(
                datetime.timedelta(minutes=kwargs["minutes"])
            )
        else:
            emails_sent = Case.objects.remind_users()
        self.stdout.write(self.style.SUCCESS("sent " + str(emails_sent) + " emails"))
