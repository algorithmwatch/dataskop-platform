import datetime

import pytest
from freezegun import freeze_time

from ..models import Case
from .factories import OngoingCaseFactory

pytestmark = pytest.mark.django_db


def test_reminder():
    OngoingCaseFactory(ongoing=4)
    assert Case.objects.all().count() == 1
    assert Case.objects.remind_users() == 0


def test_reminder_fake_date():
    """
    remind users that haven't interacted for a long time
    """
    with freeze_time("2013-12-13"):
        OngoingCaseFactory(ongoing=4, force_status=Case.Status.WAITING_USER_INPUT)
        c = OngoingCaseFactory(ongoing=4)
        c.status = Case.Status.WAITING_USER_INPUT
        c.save()
    assert Case.objects.all().count() == 2
    assert Case.objects.remind_users() == 2


def test_reminder_fake_date_no_remind():
    """
    User revceived yesterday a response so don't remind her
    """
    today = datetime.date.today()
    prev_time = today - datetime.timedelta(days=30)
    yesterday = today - datetime.timedelta(days=1)

    with freeze_time(prev_time):
        c = OngoingCaseFactory(
            ongoing=4, force_status=Case.Status.WAITING_INITIAL_EMAIL_SENT
        )
        c.status = Case.Status.WAITING_RESPONSE
        c.save()

    with freeze_time(yesterday):
        c.status = Case.Status.WAITING_USER_INPUT
        c.save()

    assert Case.objects.all().count() == 1
    assert Case.objects.remind_users() == 0


def test_reminder_fake_date_remind_and_stop():
    """
    User revceived yesterday a response so don't remind her
    """
    today = datetime.date.today()
    prev_time1 = today - datetime.timedelta(days=30)
    prev_time2 = today - datetime.timedelta(days=27)
    prev_time3 = today - datetime.timedelta(days=19)
    prev_time4 = today - datetime.timedelta(days=10)

    with freeze_time(prev_time1):
        c = OngoingCaseFactory(
            ongoing=4, force_status=Case.Status.WAITING_INITIAL_EMAIL_SENT
        )
        c.status = Case.Status.WAITING_RESPONSE
        c.save()

    assert Case.objects.all().count() == 1

    with freeze_time(prev_time2):
        c.status = Case.Status.WAITING_USER_INPUT
        c.save()

    with freeze_time(prev_time3):
        assert Case.objects.remind_users() == 1
        # don't send because we just sent an email
        assert Case.objects.remind_users() == 0

    with freeze_time(prev_time4):
        assert Case.objects.remind_users() == 1

    # don't send because we already send two emails
    assert Case.objects.remind_users() == 0
