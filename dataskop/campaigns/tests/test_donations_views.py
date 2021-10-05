import datetime
import re

import pytest
from allauth.account.models import EmailAddress
from django.contrib.auth import get_user_model
from django.core import mail
from django.urls.base import reverse
from freezegun import freeze_time

from dataskop.campaigns.models import Donation
from dataskop.campaigns.tasks import handle_donation, remind_user_registration
from dataskop.campaigns.tests.factories import CampaignFactory, DonationFactory
from dataskop.users.tests.factories import UserFactory

User = get_user_model()

pytestmark = pytest.mark.django_db


def test_confirm_all(client, django_user_model):
    user = UserFactory()

    donation = DonationFactory(unauthorized_email=user.email)

    assert django_user_model.objects.count() == 3

    assert Donation.objects.unconfirmed_by_user(user).count() == 1

    client.force_login(user)

    response = client.post(reverse("my_donations_unconfirmed"))

    assert response.status_code == 302

    assert Donation.objects.unconfirmed_by_user(user).count() == 0


def test_auto_confirm(client):
    c = CampaignFactory(status="active")
    some_email = "karlheinz@gmail.com"

    data = {
        "unauthorized_email": some_email,
        "results": {"some": "data"},
        "campaign": c.pk,
    }

    response = client.post(
        reverse("api:donations-list"),
        data=data,
        content_type="application/json",
    )

    assert response.status_code == 202

    # skip celery by calling the task directly
    handle_donation(data, "127.0.0.1")

    user = EmailAddress.objects.filter(email=some_email).first().user

    assert Donation.objects.count() > 0
    assert Donation.objects.unconfirmed_by_user(user, verified_user=False).count() == 1

    # 'click' the generated link
    magic_confirm_link = re.findall(r"(http\S*magic\S*)\s", mail.outbox[0].body)[0]
    client.get(magic_confirm_link, follow=True, REMOTE_ADDR="127.0.0.1")

    assert Donation.objects.unconfirmed_by_user(user, verified_user=False).count() == 0


def test_reminder_emails(client):

    today = datetime.date.today()
    in2days = today + datetime.timedelta(days=2)
    in3days = today + datetime.timedelta(days=3)

    c = CampaignFactory(status="active")
    some_email = "karlheinz@gmail.com"

    data = {
        "unauthorized_email": some_email,
        "results": {"some": "data"},
        "campaign": c.pk,
    }

    with freeze_time(today):
        client.post(
            reverse("api:donations-list"),
            data=data,
            content_type="application/json",
        )
        handle_donation(data, "127.0.0.1")

    with freeze_time(in2days):
        # 'click' the generated link
        magic_confirm_link = re.findall(r"(http\S*magic\S*)\s", mail.outbox[0].body)[0]
        response2 = client.get(magic_confirm_link, follow=True, REMOTE_ADDR="127.0.0.1")
        print(response2.status_code)
        assert response2.status_code == 403

    with freeze_time(in3days):
        sent_emails = remind_user_registration()

        assert sent_emails == 1

        # click on the 'go to login' link
        login_link = re.findall(r"(http\S*magic\S*)\s", mail.outbox[-1].body)[0]
        response2 = client.get(login_link, follow=True, REMOTE_ADDR="127.0.0.1")

        assert "login" in login_link

        # In prod, the form get's automatically commit on page load. Since we don't execute JS,
        # we have to post a login manually.
        client.post(
            reverse("magic_login"),
            {"email": some_email},
            follow=True,
            REMOTE_ADDR="127.0.0.1",
        )

        assert response2.status_code == 200
        # now confirm the actually confirmaiton link
        magic_confirm_link = re.findall(r"(http\S*magic\S*)\s", mail.outbox[-1].body)[0]
        response2 = client.get(magic_confirm_link, follow=True, REMOTE_ADDR="127.0.0.1")

        assert "confirm" in magic_confirm_link

        assert response2.status_code == 200

        logged_in_user = response2.context["user"]
        assert logged_in_user.email == some_email
        assert EmailAddress.objects.filter(user=logged_in_user).first().verified == True
        assert EmailAddress.objects.filter(user=logged_in_user).first().primary == True
        assert (
            EmailAddress.objects.filter(user=logged_in_user).first().email == some_email
        )

        sent_emails = remind_user_registration()

        assert sent_emails == 0
