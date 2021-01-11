import random

import factory
from django.core.management.base import BaseCommand
from django.db import transaction
from factory.django import DjangoModelFactory

from goliath.casehandling.models import (
    Case,
    CaseType,
    Entity,
    ReceivedMessage,
    SentMessage,
)
from goliath.users.models import User


class UserFactory(DjangoModelFactory):
    class Meta:
        model = User

    username = factory.Faker("name")
    email = factory.Faker("email")


class EntityFactory(DjangoModelFactory):
    class Meta:
        model = Entity

    name = factory.Faker("name")
    email = factory.Faker("company_email")
    description = factory.Faker("text")
    url = factory.Faker("url")


class CaseTypeFactory(DjangoModelFactory):
    class Meta:
        model = CaseType

    name = factory.Faker("name")
    description = factory.Faker("text")
    questions = "{}"


class CaseFactory(DjangoModelFactory):
    class Meta:
        model = Case

    answers_text = factory.Faker("text")
    email = factory.Faker("company_email")
    questions = "{}"
    answers = "{}"


class SentMessageFactory(DjangoModelFactory):
    class Meta:
        model = SentMessage

    from_email = factory.Faker("company_email")
    to_email = factory.Faker("company_email")
    subject = factory.Faker("sentence")
    content = factory.Faker("text")
    sent_at = factory.Faker("date_this_year")


class ReceivedMessageFactory(DjangoModelFactory):
    class Meta:
        model = ReceivedMessage

    from_email = factory.Faker("company_email")
    to_email = factory.Faker("company_email")
    subject = factory.Faker("sentence")
    content = factory.Faker("text")
    sent_at = factory.Faker("date_this_year")
    received_at = factory.Faker("date_this_year")
    from_display_name = factory.Faker("name")
    from_display_email = factory.Faker("email")
    spam_score = factory.Faker("pyfloat")
    to_addresses = [factory.Faker("text")]


NUM_USERS = 50
NUM_CLUBS = 10
NUM_THREADS = 12
COMMENTS_PER_THREAD = 25
USERS_PER_CLUB = 8


class Command(BaseCommand):
    help = "Generates test data"

    def add_arguments(self, parser):
        parser.add_argument(
            "--delete",
            action="store_true",
        )

        parser.add_argument(
            "--user",
            default=10,
            type=int,
        )

        parser.add_argument(
            "--entity",
            default=5,
            type=int,
        )

        parser.add_argument(
            "--case_type",
            default=10,
            type=int,
        )

        parser.add_argument(
            "--case",
            default=30,
            type=int,
        )

        parser.add_argument(
            "--message",
            default=3,
            type=int,
        )

    @transaction.atomic
    def handle(self, *args, **options):
        if options["delete"]:
            self.stdout.write("Deleting old data...")
            models = [User, Entity, Case, CaseType, SentMessage, ReceivedMessage]
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
            ct = CaseTypeFactory(entity=e)
            case_types.append(ct)

        # TODO: status
        cases = []
        for _ in range(options["case"]):
            ct = random.choice(case_types)
            u = random.choice(people)
            c = CaseFactory(case_type=ct, user=u, entity=ct.entity)

            SentMessageFactory(case=c)
            for _ in range(options["message"]):
                if random.choice([True, False]):
                    SentMessageFactory(case=c)
                else:
                    ReceivedMessageFactory(case=c)
            # cases.append(c)

        # # Add some users to clubs
        # for _ in range(NUM_CLUBS):
        #     members = random.choices(people, k=USERS_PER_CLUB)
        #     club.user.add(*members)
        #     club = ClubFactory()
        #     members = random.choices(people, k=USERS_PER_CLUB)
        #     club.user.add(*members)

        # # Create all the threads
        # for _ in range(NUM_THREADS):
        #     # Create comments for each thread
        #     for _ in range(COMMENTS_PER_THREAD):
        #         commentor = random.choice(people)
        #         CommentFactory(user=commentor, thread=thread)
