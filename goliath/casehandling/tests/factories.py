import factory
from factory.django import DjangoModelFactory

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

    name = factory.Faker("catch_phrase", locale="de")
    description = factory.Faker("text", locale="de")
    questions = "{}"


class CaseFactory(DjangoModelFactory):
    class Meta:
        model = Case

    answers_text = factory.Faker("text")
    email = factory.Faker("company_email", locale="de")
    questions = "{}"
    answers = "{}"


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
