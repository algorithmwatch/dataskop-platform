import datetime
import re

import pytest
from allauth.account.models import EmailAddress
from django.core import mail
from django.urls.base import reverse
from freezegun import freeze_time

from dataskop.campaigns.models import Donation
from dataskop.campaigns.tasks import handle_donation, remind_user_registration
from dataskop.campaigns.tests.factories import (
    CampaignFactory,
    DonationFactory,
    DonorNotificationFactory,
)
from dataskop.users.tests.factories import UserFactory


pytestmark = pytest.mark.django_db


def test_confirm_all(client, django_user_model):
    user = UserFactory()
    donation = DonationFactory(unauthorized_email=user.email)
    donation = DonationFactory(
        unauthorized_email=user.email, campaign=donation.campaign
    )

    assert Donation.objects.unconfirmed_by_user(user).count() == 2

    client.force_login(user)
    response = client.post(reverse("my_donations_unconfirmed"))
    assert response.status_code == 302

    assert Donation.objects.unconfirmed_by_user(user).count() == 0
    assert Donation.objects.confirmed_by_user(user).count() == 2
    for d in Donation.objects.confirmed_by_user(user):
        assert d.ip_address is not None


def test_auto_confirm(client):
    c = CampaignFactory(status="active")
    some_email = "karlheinz@gmail.com"

    data = {
        "unauthorized_email": some_email,
        "results": {"some": "data"},
        "campaign": c.pk,
    }

    # The celery tasks gets executed eagerly.
    response = client.post(
        reverse("api:donations-list"),
        data=data,
        content_type="application/json",
    )

    assert response.status_code == 202

    user = EmailAddress.objects.filter(email=some_email).first().user

    assert Donation.objects.count() > 0
    assert Donation.objects.unconfirmed_by_user(user, verified_user=False).count() == 1

    # 'click' the generated link
    magic_confirm_link = re.findall(r"(http\S*magic\S*)\s", mail.outbox[0].body)[0]
    client.get(magic_confirm_link, follow=True, REMOTE_ADDR="127.0.0.1")

    assert Donation.objects.unconfirmed_by_user(user, verified_user=False).count() == 0
    assert Donation.objects.confirmed_by_user(user).first().ip_address is not None


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
        assert response2.status_code == 403

    with freeze_time(in3days):
        sent_emails = remind_user_registration()

        assert sent_emails == 1

        # extract the magic link from the second last email, the last is the admin
        # notification
        login_link = re.findall(r"(http\S*magic\S*)\s", mail.outbox[-2].body)[0]
        # click on the 'go to login' link
        response2 = client.get(login_link, follow=True, REMOTE_ADDR="127.0.0.1")

        assert "login" in login_link

        # In prod, the form get's automatically commit on page load. Since we don't
        # execute JS, we have to post a login manually.
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
        assert EmailAddress.objects.filter(user=logged_in_user).first().verified is True
        assert EmailAddress.objects.filter(user=logged_in_user).first().primary is True
        assert (
            EmailAddress.objects.filter(user=logged_in_user).first().email == some_email
        )

        sent_emails = remind_user_registration()

        assert sent_emails == 0


def test_donor_notification_views(client):
    today = datetime.date.today()
    in1month = today + datetime.timedelta(days=30)

    cam = CampaignFactory()
    DonationFactory(email__verified=True, campaign=cam)
    donor_noti_1 = DonorNotificationFactory(campaign=cam, subject="Test 1", draft=False)

    disable_notification_link = re.findall(
        r"(http\S*abbestellen\S*)\s", mail.outbox[-1].body
    )[0]

    assert len([m for m in mail.outbox if m.subject == donor_noti_1.subject]) == 1

    with freeze_time(in1month):
        client.get(disable_notification_link, follow=True, REMOTE_ADDR="127.0.0.1")

        response2 = client.post(
            disable_notification_link,
            {"disable": True},
            follow=True,
            REMOTE_ADDR="127.0.0.1",
        )

        assert response2.status_code == 200

        donor_noti_2 = DonorNotificationFactory(
            campaign=cam, subject="Test 2", draft=False
        )
        assert len([m for m in mail.outbox if m.subject == donor_noti_2.subject]) == 0
