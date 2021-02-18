import pytest

from ..models import Status
from .factories import CaseTypeFactoryWithEntitiesFactory, OngoingCaseFactory

pytestmark = pytest.mark.django_db


def test_factories():
    cte = CaseTypeFactoryWithEntitiesFactory(entities=4)
    assert cte.entities.all().count() == 4

    cte2 = CaseTypeFactoryWithEntitiesFactory(entities=3)
    assert cte2.entities.all().count() == 3

    c = OngoingCaseFactory(ongoing=4)
    assert len(c.all_messages) == 5
    assert c.user.email is not None


def test_factories_status():
    ctes = OngoingCaseFactory.create_batch(
        20, ongoing=4, force_status=Status.WAITING_USER_INPUT
    )
    for c in ctes:
        assert c.status == Status.WAITING_USER_INPUT
