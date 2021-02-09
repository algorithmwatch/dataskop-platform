import random
from pathlib import Path

import factory
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import transaction
from django.db.models import signals

from goliath.casehandling.models import (
    Case,
    CaseType,
    Entity,
    ReceivedMessage,
    SentMessage,
    Status,
)
from goliath.casehandling.tests.factories import (
    CaseFactory,
    CaseTypeFactory,
    EntityFactory,
    ReceivedMessageFactory,
    SentMessageFactory,
)
from goliath.users.tests.factories import UserFactory

User = get_user_model()


class Command(BaseCommand):
    help = "Generates test data"

    def add_arguments(self, parser):
        parser.add_argument(
            "--delete",
            action="store_true",
        )

        parser.add_argument(
            "--user",
            default=5,
            type=int,
        )

        parser.add_argument(
            "--entity",
            default=3,
            type=int,
        )

        parser.add_argument(
            "--case_type",
            default=5,
            type=int,
        )

        parser.add_argument(
            "--case",
            default=10,
            type=int,
        )

        parser.add_argument(
            "--message",
            default=2,
            type=int,
        )

    # mute signals when creating fake data (via https://stackoverflow.com/a/26490827/4028896)

    @factory.django.mute_signals(signals.pre_save, signals.post_save)
    @transaction.atomic
    def handle(self, *args, **options):
        questions = Path(
            "/app/goliath/casehandling/management/commands/questions.json"
        ).read_text()

        if options["delete"]:
            self.stdout.write("Deleting old data (besides superusers)...")

            User.objects.filter(is_superuser=False).delete()
            models = [Entity, Case, CaseType, SentMessage, ReceivedMessage]
            for m in models:
                m.objects.all().delete()

        self.stdout.write("Creating new data...")

        # Create all the users
        people = []
        for _ in range(options["user"]):
            person = UserFactory()
            people.append(person)

        entities = []
        for _ in range(options["entity"]):
            e = EntityFactory()
            entities.append(e)

        case_types = []
        for _ in range(options["case_type"]):
            e = random.choice(entities)
            ct = CaseTypeFactory(questions=questions)
            ct.entities.add(e)
            case_types.append(ct)

        cases = []
        for _ in range(options["case"]):
            ct = random.choice(case_types)
            u = random.choice(list(User.objects.filter(is_staff=True)))
            status = random.choice(Status.choices)[0]

            # choosen all entities
            c = CaseFactory(case_type=ct, user=u, status=status)
            c.selected_entities.add(*ct.entities.all())

            SentMessageFactory(case=c)
            for _ in range(options["message"]):
                if random.choice([True, False]):
                    SentMessageFactory(case=c)
                else:
                    ReceivedMessageFactory(case=c)

            cases.append(c)
        self.stdout.write(self.style.SUCCESS("done"))
