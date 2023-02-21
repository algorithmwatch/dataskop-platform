import re
from unittest import mock

import pytest
from django.contrib.sites.models import Site
from django.core import mail

from dataskop.campaigns.tests.factories import SiteExtendedFactory
from dataskop.mailjetsync.models import NewsletterSubscription

pytestmark = pytest.mark.django_db


@mock.patch(
    "dataskop.mailjetsync.mailjet.subscribe_mailjet_list",
)
def test_double_optin(mock_mailjet_create, client):
    SiteExtendedFactory(site=Site.objects.first())

    some_email = "hi+djangotest@jfilter.de"

    data = {
        "email": some_email,
        "has_donated": True,
        "needs_double_optin": True,
    }

    response_1 = client.post(
        "/api/mailjetsync/",
        data=data,
        content_type="application/json",
    )

    assert response_1.status_code == 202
    assert NewsletterSubscription.objects.count() == 1

    response_2 = client.post(
        "/api/mailjetsync/",
        data=data,
        content_type="application/json",
    )
    assert response_2.status_code == 202
    assert NewsletterSubscription.objects.count() == 1
    assert not NewsletterSubscription.objects.first().confirmed

    # 'click' the generated link
    magic_confirm_link = re.findall(r"(http\S*magic\S*)\s", mail.outbox[0].body)[0]
    response_3 = client.get(magic_confirm_link, follow=False, REMOTE_ADDR="127.0.0.1")

    assert NewsletterSubscription.objects.first().confirmed
    assert response_3.status_code == 302

    # Check if mock worked
    mock_mailjet_create.assert_called_with(some_email, data["has_donated"])

    # 'click' the generated link again
    magic_confirm_link = re.findall(r"(http\S*magic\S*)\s", mail.outbox[0].body)[0]
    response_4 = client.get(magic_confirm_link, follow=False, REMOTE_ADDR="127.0.0.1")
    assert response_4.status_code == 403
