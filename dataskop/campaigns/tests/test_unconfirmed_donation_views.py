from allauth.account.models import EmailAddress
from django.urls.base import reverse

from dataskop.campaigns.models import Donation
from dataskop.campaigns.tests.factories import DonationFactory


def test_with_authenticated_client(client, django_user_model):
    user = django_user_model.objects.create_user(
        email="2test@test.com", first_name="Johanna", last_name="John"
    )
    EmailAddress.objects.create(
        user=user, email=user.email, primary=True, verified=True
    )

    donation = DonationFactory(unauthorized_email=user.email)

    assert Donation.objects.unconfirmed_donations_by_user(user).count() == 1

    client.force_login(user)

    response = client.post(reverse("my-donations-unconfirmed"))

    assert response.status_code == 302

    assert Donation.objects.unconfirmed_donations_by_user(user).count() == 0
