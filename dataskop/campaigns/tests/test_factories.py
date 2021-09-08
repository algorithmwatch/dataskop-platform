import pytest
from allauth.account.models import EmailAddress
from django.db.models.expressions import F

from .factories import DonationFactory

pytestmark = pytest.mark.django_db


def test_donation_factory():
    d1 = DonationFactory()
    d2 = DonationFactory(email__verified=True)
    d3 = DonationFactory(email__verified=False)

    assert d1.donor is None
    assert d2.donor is not None
    assert d3.donor is None
