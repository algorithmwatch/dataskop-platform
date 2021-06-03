import pytest
from allauth.account.models import EmailAddress
from django.contrib.auth import get_user_model
from django.core import mail

from .factories import DonationFactory

pytestmark = pytest.mark.django_db

User = get_user_model()


def test_multiple_donation_by_same_user():
    # create a new donation campaing (including a new admin user)
    donation1 = DonationFactory()

    d_email = EmailAddress.objects.filter(email=donation1.unauthorized_email).all()
    assert d_email.count() == 1
    assert d_email.first().verified == False
    assert len(mail.outbox), 2

    # - use the same email so a new user does not get created
    # - but one more email is send to the user
    assert User.objects.all().count() == 3  # including Anonymous User
    donation2 = DonationFactory(
        unauthorized_email=donation1.unauthorized_email,
        campaign=donation1.campaign,
    )
    assert User.objects.all().count() == 3  # including Anonymous User
    assert len(mail.outbox), 3
