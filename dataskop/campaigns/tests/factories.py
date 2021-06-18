import json
import random
from typing import Any, Sequence

import factory
from factory import Faker, post_generation
from factory.django import DjangoModelFactory

from dataskop.campaigns.models import Campaign, Donation, Provider, StatusOptions
from dataskop.users.tests.factories import UserFactory


def gen_fake_json(_):
    return json.loads(Faker("json").generate())


class ProviderFactory(DjangoModelFactory):
    name = Faker("word")

    class Meta:
        model = Provider


class CampaignFactory(DjangoModelFactory):
    status = factory.LazyAttribute(
        lambda o: random.choice(list(StatusOptions.STATUS_OPTIONS))[0]
    )
    title = Faker("word")
    description = Faker("text")
    scraping_config = factory.LazyAttribute(gen_fake_json)
    created_by = factory.SubFactory(UserFactory)
    provider = factory.SubFactory(ProviderFactory)

    class Meta:
        model = Campaign


class DonationFactory(DjangoModelFactory):
    campaign = factory.SubFactory(CampaignFactory)
    unauthorized_email = Faker("email")
    results = factory.LazyAttribute(gen_fake_json)

    class Meta:
        model = Donation
