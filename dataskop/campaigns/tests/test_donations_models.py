import datetime

import pytest
from allauth.account.models import EmailAddress
from django.contrib.auth import get_user_model
from django.core import mail
from freezegun.api import freeze_time

from dataskop.campaigns.models import Donation
from dataskop.campaigns.tasks import remind_user_registration

from .factories import CampaignFactory, DonationFactory

pytestmark = pytest.mark.django_db

User = get_user_model()


def test_multiple_donation_by_same_user():
    # create a new donation campaing (not campaign video)
    cam = CampaignFactory(created_by=None)
    donation1 = DonationFactory(campaign=cam)

    d_email = EmailAddress.objects.filter(email=donation1.unauthorized_email).all()
    assert d_email.count() == 1
    assert d_email.first().verified == False

    assert len(mail.outbox) == 1

    # - use the same email so a new user does not get created
    # - but one more email is send to the user
    assert User.objects.all().count() == 2  # including Anonymous User
    donation2 = DonationFactory(
        unauthorized_email=donation1.unauthorized_email,
        campaign=donation1.campaign,
    )
    assert User.objects.all().count() == 2  # including Anonymous User
    assert len(mail.outbox) == 2

    #  same donation, but only one email per hour should be sent
    donation3 = DonationFactory(
        unauthorized_email=donation1.unauthorized_email,
        campaign=donation1.campaign,
    )

    assert len(mail.outbox) == 2


def test_user_delete():
    d = DonationFactory(email__verified=True)

    assert Donation.objects.count() == 1

    num_deleted, _ = User.objects.filter(email=d.unauthorized_email).delete()

    assert num_deleted == 3

    assert Donation.objects.count() == 0


def test_reminders_active():
    # create a new donation campaing (not campaign video)
    cam = CampaignFactory(created_by=None, status="active")
    donation1 = DonationFactory(campaign=cam)

    d_email = EmailAddress.objects.filter(email=donation1.unauthorized_email).all()
    assert d_email.count() == 1
    assert d_email.first().verified == False

    assert len(mail.outbox) == 1

    remind_user_registration()
    remind_user_registration()
    remind_user_registration()
    assert len(mail.outbox) == 4

    remind_user_registration()
    remind_user_registration()
    remind_user_registration()
    remind_user_registration()
    remind_user_registration()
    remind_user_registration()
    remind_user_registration()
    remind_user_registration()
    remind_user_registration()
    remind_user_registration()
    remind_user_registration()
    remind_user_registration()
    assert len(mail.outbox) == 11  # 10 notificaiton + 1 user confirm email


def test_reminders_inactive():
    # create a new donation campaing (not campaign video)
    cam = CampaignFactory(created_by=None, status="inactive")
    donation1 = DonationFactory(campaign=cam)

    d_email = EmailAddress.objects.filter(email=donation1.unauthorized_email).all()
    assert d_email.count() == 1
    assert d_email.first().verified == False

    assert len(mail.outbox) == 1

    remind_user_registration()
    remind_user_registration()
    remind_user_registration()
    assert len(mail.outbox) == 1


def test_reminders_cam_none():
    donation1 = DonationFactory(campaign=None)

    d_email = EmailAddress.objects.filter(email=donation1.unauthorized_email).all()
    assert d_email.count() == 1
    assert d_email.first().verified == False

    assert len(mail.outbox) == 1

    remind_user_registration()
    remind_user_registration()
    remind_user_registration()
    assert len(mail.outbox) == 1


def test_delete_unconfirmed_donations():

    today = datetime.date.today()
    in2days = today + datetime.timedelta(days=2)
    in3days = today + datetime.timedelta(days=3)

    with freeze_time(today):
        donation1 = DonationFactory(campaign=None)
        donation2 = DonationFactory(campaign=None)
        donation3 = DonationFactory(campaign=None, email__verified=True)
        donation4 = DonationFactory(campaign=None, email__verified=True)

        donation4_non_confirm = DonationFactory(
            campaign=None, unauthorized_email=donation4.unauthorized_email
        )

        donation2_dupli = DonationFactory(
            campaign=None, unauthorized_email=donation2.unauthorized_email
        )

        # no deletion for donations that were recently created (<24h)
        del_objs = Donation.objects.delete_unconfirmed_donations()
        assert del_objs == {}

    with freeze_time(in2days):
        # no deletion if a donor is assigned, testing if given donation_qs works
        assert {} == Donation.objects.delete_unconfirmed_donations(
            donation_qs=Donation.objects.filter(donor__isnull=False)
        )

        del_objs = Donation.objects.delete_unconfirmed_donations()
        assert (
            sum(del_objs.values()) == 7
        )  # 2 unique donations (donation + email + user = 3 x 2) + another duplicate donation = 7
        assert Donation.objects.count() == 3
        assert EmailAddress.objects.filter(email=donation4.unauthorized_email).exists()
        assert User.objects.filter(email=donation4.unauthorized_email).exists()
        # do not delete unconfirmed donations if the email is already verified (but not assiged to the second donation)
        assert (
            Donation.objects.filter(
                unauthorized_email=donation4.unauthorized_email
            ).count()
            == 2
        )

        assert not EmailAddress.objects.filter(
            email=donation1.unauthorized_email
        ).exists()
        assert not User.objects.filter(email=donation1.unauthorized_email).exists()

        donation5 = DonationFactory(campaign=None)

        assert {} == Donation.objects.delete_unconfirmed_donations()

    with freeze_time(in3days):
        del_objs = Donation.objects.delete_unconfirmed_donations(
            donation_qs=Donation.objects.filter(donor__isnull=True)
        )
        assert sum(del_objs.values()) == 3
