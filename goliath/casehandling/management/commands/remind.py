from django.core.management.base import BaseCommand, CommandError

from ...models import Case


class Command(BaseCommand):
    help = "remind users or entities to sent a response"

    def add_arguments(self, parser):
        parser.add_argument(
            "whom_to_remind",
            type=str,
            help="`./manage.py remind user` or `./manage.py remind entity`",
        )

    def handle(self, **kwargs):
        if kwargs["whom_to_remind"] in ("user", "users"):
            self.stdout.write("check for people who need a reminder")
            emails_sent = Case.objects.remind_users()

        if kwargs["whom_to_remind"] in ("entity", "entities"):
            self.stdout.write("check for entities who need a reminder")
            emails_sent = Case.objects.remind_entities()

        try:
            self.stdout.write(
                self.style.SUCCESS("sent " + str(emails_sent) + " emails")
            )
        except:
            raise CommandError(
                "do it like this: `./manage.py remind user` or `./manage.py remind entity`"
            )
