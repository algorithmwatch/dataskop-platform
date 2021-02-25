import random

import factory
import factory.fuzzy
from factory.django import DjangoModelFactory

from goliath.users.tests.factories import UserFactory

from ..models import Case, CaseType, Entity, ReceivedMessage, SentMessage


class EntityFactory(DjangoModelFactory):
    class Meta:
        model = Entity

    name = factory.Faker("company", locale="de")
    email = factory.Faker("company_email", locale="de")
    description = factory.Faker("text", locale="de")
    url = factory.Faker("url", locale="de")


class CaseTypeFactory(DjangoModelFactory):
    class Meta:
        model = CaseType

    title = factory.fuzzy.FuzzyText(length=15)
    claim = factory.Faker("catch_phrase", locale="de")
    short_description = factory.Faker("catch_phrase", locale="de")
    description = factory.Faker("text", locale="de")
    questions = {}


class CaseTypeFactoryWithEntitiesFactory(CaseTypeFactory):
    @factory.post_generation
    def entities(self, create, extracted: int = 3, **kwargs):
        """
        called like CaseTypeFactoryWithEntitiesFactory(entities=4)
        """
        if not create:
            # Build, not create related
            return

        if extracted:
            for _ in range(extracted):
                self.entities.add(EntityFactory())


class CaseFactory(DjangoModelFactory):
    class Meta:
        model = Case

    answers_text = factory.Faker("text")
    email = factory.Faker("company_email", locale="de")
    questions = {}
    answers = {}


class OngoingCaseFactory(CaseFactory):
    user = factory.SubFactory(UserFactory)
    status = factory.LazyAttribute(
        lambda o: random.choice(Case.Status.choices)[0]
        if o.force_status is None
        else o.force_status
    )

    class Params:
        force_status = None

    @factory.post_generation
    def ongoing(self, create, extracted: int = 3, **kwargs):
        """
        called like CaseTypeFactoryWithEntitiesFactory(entities=4)
        """
        if not create:
            # Build, not create related
            return

        self.save()

        if extracted:
            self.case_type = CaseTypeFactoryWithEntitiesFactory(entities=extracted)
            self.selected_entities.add(*self.case_type.entities.all())

            SentMessageFactory(case=self)
            for _ in range(extracted):
                if random.choice([True, False]):
                    SentMessageFactory(case=self)
                else:
                    ReceivedMessageFactory(case=self)


class SentMessageFactory(DjangoModelFactory):
    class Meta:
        model = SentMessage

    from_email = factory.Faker("email", locale="de")
    to_email = factory.Faker("company_email", locale="de")
    subject = factory.Faker("sentence")
    content = factory.Faker("text")
    sent_at = factory.Faker("date_this_year")


class ReceivedMessageFactory(DjangoModelFactory):
    class Meta:
        model = ReceivedMessage

    from_email = factory.Faker("company_email", locale="de")
    to_email = factory.Faker("email", locale="de")
    subject = factory.Faker("sentence")
    content = factory.Faker("text")
    sent_at = factory.Faker("date_this_year")
    received_at = factory.Faker("date_this_year")
    from_display_name = factory.Faker("company", locale="de")
    from_display_email = factory.Faker("company_email", locale="de")
    spam_score = factory.Faker("pyfloat")
    to_addresses = [factory.Faker("email")]
