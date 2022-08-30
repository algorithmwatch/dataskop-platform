import re

import pytest
from allauth.account.models import EmailAddress
from django.contrib.auth import get_user_model
from django.core import mail
from django.urls.base import reverse
from django.contrib.sites.models import Site

from dataskop.campaigns.models import SiteExtended
from dataskop.campaigns.tests.factories import SiteExtendedFactory

User = get_user_model()

pytestmark = pytest.mark.django_db


# Arrange
@pytest.fixture
def setupSiteExtended():
    if SiteExtended.objects.count() == 0:
        SiteExtendedFactory(site=Site.objects.first())


def test_magic_login(setupSiteExtended, client, django_user_model):
    r1 = client.get(reverse("magic_login"))
    assert r1.status_code == 200

    num_user_before = django_user_model.objects.count()

    the_email = "peter@lustig.de"
    r2 = client.post(
        reverse("magic_login"),
        {"email": the_email},
        follow=True,
        REMOTE_ADDR="127.0.0.1",
    )

    assert r2.status_code == 200
    assert django_user_model.objects.count() == num_user_before + 1
    assert len(mail.outbox) == 1

    links = re.findall(r"(http\S*magic\S*)\s", mail.outbox[0].body)

    the_url = links[0]
    r3 = client.get(the_url, follow=True, REMOTE_ADDR="127.0.0.1")

    logged_in_user = r3.context["user"]
    assert logged_in_user.email == the_email
    assert EmailAddress.objects.filter(user=logged_in_user).first().verified == True
    assert EmailAddress.objects.filter(user=logged_in_user).first().primary == True
    assert EmailAddress.objects.filter(user=logged_in_user).first().email == the_email


def test_magic_login_rate_limit(setupSiteExtended, client, django_user_model):
    # test rate limitting
    limited = False
    for _ in range(20):
        r = client.post(
            reverse("magic_login"), {"email": "peter@lustig.de"}, follow=True
        )
        if r.status_code != 200:
            assert r.status_code == 403
            limited = True
            break
    assert limited
