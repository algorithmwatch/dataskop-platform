from django.core.management.base import BaseCommand
from django.core.management.color import no_style
from django.db import connection, transaction

from dataskop.mailjetsync.mailjet import (
    create_contact_meta,
    get_contact_meta,
    subscribe_mailjet_list,
    verify_emails,
)


class Command(BaseCommand):
    help = "Generate fake data to get started quickly"

    def add_arguments(self, parser):
        parser.add_argument("--email", type=str)
        parser.add_argument(
            "--get_meta",
            action="store_true",
        )
        parser.add_argument(
            "--create_meta",
            action="store_true",
        )
        parser.add_argument(
            "--verify",
            action="store_true",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        if options["get_meta"]:
            get_contact_meta()
            return

        if options["create_meta"]:
            create_contact_meta()
            return

        if options["verify"]:
            verify_emails()
            return

        if not options["email"]:
            self.stdout.write("Email is not set. Aborting")
        else:
            self.stdout.write("Adding email to mailjet list.")
            subscribe_mailjet_list(options["email"])

            self.stdout.write(self.style.SUCCESS("done"))
