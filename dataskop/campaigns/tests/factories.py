import json
import random
from typing import Any, Sequence

import factory
from allauth.account.models import EmailAddress
from factory import Faker
from factory.django import DjangoModelFactory

from dataskop.campaigns.models import (
    Campaign,
    Donation,
    DonorNotification,
    DonorNotificationSetting,
    Provider,
    StatusOptions,
)
from dataskop.users.tests.factories import UserFactory


def gen_fake_json(_):
    return json.loads(Faker("json").evaluate(None, None, {"locale": None}))


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
    ip_address = Faker("ipv4")

    class Meta:
        model = Donation

    @factory.post_generation
    def email(obj, create: bool, extracted: Sequence[Any], **kwargs):
        if create:
            verified = "verified" in kwargs and kwargs["verified"]
            if verified:
                email_obj = EmailAddress.objects.filter(
                    email=obj.unauthorized_email
                ).first()
                email_obj.set_as_primary(conditional=True)
                email_obj.verified = True
                email_obj.save()
                obj.donor = email_obj.user
                obj.save()


class DonorNotificationSettingFactory(DjangoModelFactory):
    user = factory.SubFactory(UserFactory)
    disable_all = False

    class Meta:
        model = DonorNotificationSetting

    @factory.post_generation
    def disabled_campaigns(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            for c in extracted:
                self.disabled_campaigns.add(c)


class DonorNotificationFactory(DjangoModelFactory):
    sent_by = factory.SubFactory(UserFactory)
    subject = Faker("text", max_nb_chars=100)
    text = Faker("text")

    class Meta:
        model = DonorNotification
