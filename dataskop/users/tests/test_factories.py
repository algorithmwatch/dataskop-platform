import pytest
from allauth.account.models import EmailAddress

from .factories import UserFactory

pytestmark = pytest.mark.django_db


def test_user_factory():
    user = UserFactory()
    assert user.full_name == user.first_name + " " + user.last_name

    assert EmailAddress.objects.filter(user=user).first().email == user.email

    user_unconfirmed = UserFactory(email_obj__verified=False)
    assert EmailAddress.objects.filter(user=user_unconfirmed).first().verified is False

    user_confirmed = UserFactory(email_obj__verified=True)
    assert EmailAddress.objects.filter(user=user_confirmed).first().verified is True
