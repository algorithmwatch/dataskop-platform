import random
from typing import Any, Sequence

import factory
from factory import Faker, post_generation
from factory.django import DjangoModelFactory

from dataskop.campaigns.models import Campaign, Donation, StatusOptions
from dataskop.users.tests.factories import UserFactory


class CampaignFactory(DjangoModelFactory):
    status = factory.LazyAttribute(
        lambda o: random.choice(list(StatusOptions.STATUS_OPTIONS))[0]
    )
    title = Faker("word")
    description = Faker("text")
    scraper_config = Faker("json")
    created_by = factory.SubFactory(UserFactory)

    class Meta:
        model = Campaign


class DonationFactory(DjangoModelFactory):
    campaign = factory.SubFactory(CampaignFactory)
    unauthorized_email = Faker("email")
    results = Faker("json")

    class Meta:
        model = Donation
