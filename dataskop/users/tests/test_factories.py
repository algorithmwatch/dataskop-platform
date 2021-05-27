import pytest

from .factories import UserFactory

pytestmark = pytest.mark.django_db


def test_user_factory():
    user = UserFactory()
    assert user.full_name == user.first_name + " " + user.last_name
