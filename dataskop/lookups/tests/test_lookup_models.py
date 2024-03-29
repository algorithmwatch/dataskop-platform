import pytest

from dataskop.campaigns.tests.factories import DonationFactory
from dataskop.lookups.models import LookupJob

pytestmark = pytest.mark.django_db


def test_lookup_from_donation(client):
    DonationFactory()
    d = DonationFactory(
        results={"lookups": {"id3": "data", "id4": "data"}, "dump": "data"},
        email__verified=True,
    )

    assert d.results["lookups"] is None
    assert (
        LookupJob.objects.filter(input_done={"id3": "data", "id4": "data"}).count() == 1
    )
    assert LookupJob.objects.count() == 1
