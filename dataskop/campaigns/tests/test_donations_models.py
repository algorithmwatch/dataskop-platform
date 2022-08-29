import datetime

import pytest
from allauth.account.models import EmailAddress
from django.core import mail
from freezegun.api import freeze_time

from dataskop.campaigns.models import Donation, Event
from dataskop.campaigns.tasks import remind_user_registration
from dataskop.users.models import User


from .factories import (
    CampaignFactory,
    DonationFactory,
    DonorNotificationFactory,
    DonorNotificationSettingFactory,
)

pytestmark = pytest.mark.django_db


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
    don = Donation.objects.all().values()[0]

    user = User.objects.filter(email=d.unauthorized_email).values()[0]
    assert user
    num_deleted, _ = User.objects.filter(email=d.unauthorized_email).first().delete()

    assert num_deleted == 3
    assert Donation.objects.count() == 0

    assert Event.objects.count() == 1
    assert Event.objects.first().message == "user deleted"
    assert Event.objects.first().data["user"] == user["id"]
    assert len(Event.objects.first().data["donations"]) == 1
    assert Event.objects.first().data["donations"][0]["id"] == don["id"]
    assert Event.objects.first().data["donations"][0]["campaign"] == don["campaign_id"]


def test_reminders_active():
    cam = CampaignFactory(created_by=None, status="active")
    donation1 = DonationFactory(campaign=cam)

    d_email = EmailAddress.objects.filter(email=donation1.unauthorized_email).all()
    assert d_email.count() == 1
    assert d_email.first().verified == False

    assert len(mail.outbox) == 1

    remind_user_registration()
    remind_user_registration()
    remind_user_registration()
    assert len(mail.outbox) == 4 + 3  # 4 reminders, 3 admin notification

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
    assert len(mail.outbox) == 10 + 1 + 10  # 10 notificaiton + 1 user confirm email


def test_reminders_inactive():
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
    c = CampaignFactory(status="active")
    donation1 = DonationFactory(campaign=c)
    donation1.campaign = None
    donation1.save()

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

    cam = CampaignFactory()

    with freeze_time(today):
        donation1 = DonationFactory(campaign=cam)
        donation2 = DonationFactory(campaign=cam)
        donation3 = DonationFactory(campaign=cam, email__verified=True)
        donation4 = DonationFactory(campaign=cam, email__verified=True)

        donation4_non_confirm = DonationFactory(
            campaign=cam, unauthorized_email=donation4.unauthorized_email
        )

        donation2_dupli = DonationFactory(
            campaign=cam, unauthorized_email=donation2.unauthorized_email
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

        donation5 = DonationFactory(campaign=cam)

        assert {} == Donation.objects.delete_unconfirmed_donations()

    with freeze_time(in3days):
        # donation where the email was already deleted
        donation6 = DonationFactory(campaign=cam)
        EmailAddress.objects.filter(email=donation6.unauthorized_email).delete()

        # a anonymous donation without any email should not get deleted
        donation7 = DonationFactory(campaign=cam, unauthorized_email=None)

        del_objs = Donation.objects.delete_unconfirmed_donations(
            donation_qs=Donation.objects.filter(donor__isnull=True)
        )
        assert (
            sum(del_objs.values()) == 4
        )  # (3 for donation5 + 1 for donation6 + 0 for donation7)


def test_delete_anonymous_donations():
    cam = CampaignFactory()

    DonationFactory(campaign=cam, unauthorized_email=None)
    DonationFactory(campaign=cam)
    DonationFactory()

    assert Donation.objects.delete_anonymous_donations() == 1


def test_donor_notification_models():
    cam = CampaignFactory()
    d1 = DonationFactory(email__verified=True, campaign=cam)
    d2 = DonationFactory(email__verified=True, campaign=cam)
    # re-use exiting user for d3
    d3 = DonationFactory(
        email__verified=True, campaign=cam, unauthorized_email=d2.donor.email
    )

    d4_disable_all = DonationFactory(email__verified=True, campaign=cam)
    d5_disabled_noti = DonationFactory(email__verified=True, campaign=cam)
    d6_unrelated = DonationFactory(email__verified=True)

    donor_noti_1 = DonorNotificationFactory(campaign=cam, subject="Test 1")

    assert len([m for m in mail.outbox if "DRAFT" in m.subject]) == 1

    donor_noti_1.draft = False
    donor_noti_1.save()

    assert len([m for m in mail.outbox if m.subject == donor_noti_1.subject]) == 4

    dn_settings_1 = DonorNotificationSettingFactory(
        user=d4_disable_all.donor, disable_all=True
    )
    dn_settings_2 = DonorNotificationSettingFactory(
        user=d5_disabled_noti.donor,
        disable_all=False,
        disabled_campaigns=[cam, CampaignFactory()],
    )

    donor_noti_2 = DonorNotificationFactory(campaign=cam, subject="Test 2", draft=False)
    assert len([m for m in mail.outbox if m.subject == donor_noti_2.subject]) == 2

    dn_settings_2.disabled_campaigns.remove(cam)

    donor_noti_3 = DonorNotificationFactory(campaign=cam, subject="Test 3", draft=False)
    assert len([m for m in mail.outbox if m.subject == donor_noti_3.subject]) == 3
