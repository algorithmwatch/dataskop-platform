from typing import Any, Sequence

import factory
from allauth.account.models import EmailAddress
from django.contrib.auth import get_user_model
from factory import Faker
from factory.django import DjangoModelFactory


class EmailFactory(DjangoModelFactory):
    verified = True
    primary = True
    email = None
    user = None

    class Meta:
        model = EmailAddress


class UserFactory(DjangoModelFactory):
    first_name = Faker("first_name", locale="de")
    last_name = Faker("last_name", locale="de")
    email = Faker("email", locale="de")

    @factory.post_generation
    def setup(obj, create: bool, extracted: Sequence[Any], **kwargs):
        password = (
            extracted
            if extracted
            else Faker(
                "password",
                length=42,
                special_chars=True,
                digits=True,
                upper_case=True,
                lower_case=True,
            ).evaluate(None, None, extra={"locale": None})
        )
        obj.set_password(password)

        if create:
            EmailFactory(email=obj.email, user=obj)

    class Meta:
        model = get_user_model()
        django_get_or_create = ["first_name", "last_name"]
