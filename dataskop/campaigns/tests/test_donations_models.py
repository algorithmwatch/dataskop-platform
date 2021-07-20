import pytest
from allauth.account.models import EmailAddress
from django.contrib.auth import get_user_model
from django.core import mail

from dataskop.campaigns.models import Donation
from dataskop.campaigns.tasks import remind_user_registration
from dataskop.users.tests.factories import UserFactory

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
    user = UserFactory()
    d = DonationFactory(donor=user, unauthorized_email=None)

    assert Donation.objects.count() == 1

    user.delete()

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
    assert len(mail.outbox) == 6  # 5 notificaiton + 1 user confirm email


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
