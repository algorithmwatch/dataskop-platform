import pytest
from allauth.account.models import EmailAddress
from django.contrib.auth import get_user_model
from django.core import mail
from django.urls.base import reverse

from dataskop.campaigns.models import Campaign, Donation
from dataskop.campaigns.signals import handle_verified
from dataskop.campaigns.tasks import handle_donation
from dataskop.campaigns.tests.factories import CampaignFactory, DonationFactory
from dataskop.users.signals import post_magic_email_verified
from dataskop.users.tests.factories import UserFactory

User = get_user_model()

pytestmark = pytest.mark.django_db


def test_confirm_all(client, django_user_model):
    user = UserFactory()

    donation = DonationFactory(unauthorized_email=user.email)

    assert django_user_model.objects.count() == 3

    assert Donation.objects.unconfirmed_donations_by_user(user).count() == 1

    client.force_login(user)

    response = client.post(reverse("my_donations_unconfirmed"))

    assert response.status_code == 302

    assert Donation.objects.unconfirmed_donations_by_user(user).count() == 0


def test_auto_confirm(client):
    c = CampaignFactory()
    some_email = "karlheinz@gmail.com"

    data = {
        "unauthorized_email": some_email,
        "results": {"some": "data"},
        "campaign": c.pk,
    }

    response = client.post(
        reverse("api:donate-list"),
        data=data,
        content_type="application/json",
    )

    assert response.status_code == 202

    handle_donation(data)

    user = EmailAddress.objects.filter(email=some_email).first().user

    assert Donation.objects.count() > 0
    assert (
        Donation.objects.unconfirmed_donations_by_user(
            user, verified_user=False
        ).count()
        == 1
    )

    handle_verified(user, request=None, user=user, email=some_email)

    assert (
        Donation.objects.unconfirmed_donations_by_user(
            user, verified_user=False
        ).count()
        == 0
    )
