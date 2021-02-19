import datetime

from django.db import models

from ..utils.time import date_within_margin


class CaseManager(models.Manager):
    def remind_users(
        self,
        margin: datetime.timedelta = datetime.timedelta(days=7),
        max_reminders: int = 2,
    ):
        """
        Iterate over all user and check if they should get a reminder.
        Default: remind after 7 days, then remind again after 7 days and stop.
        """

        emails_sent = 0
        for case in self.filter(
            status=self.model.Status.WAITING_USER_INPUT,
            sent_user_reminders__lt=max_reminders,
        ):
            if case.last_user_reminder_sent_at is not None and date_within_margin(
                case.last_user_reminder_sent_at, margin
            ):
                continue

            last_action_date = case.last_action_at
            if last_action_date is not None:
                # there was a status change
                if not date_within_margin(last_action_date, margin):
                    # and there was no status update for at least $margin time
                    case.send_user_reminder()
                    emails_sent += 1
        return emails_sent

    def remind_entities(
        self,
        margin: datetime.timedelta = datetime.timedelta(days=7),
        max_reminders: int = 2,
    ):
        """
        Iterate over all user and check if they should get a reminder.
        Default: remind after 7 days, then remind again after 7 days and stop.
        """

        emails_sent = 0
        for case in self.filter(
            status=self.model.Status.WAITING_RESPONSE,
            sent_entities_reminders__lt=max_reminders,
        ):
            if case.last_entities_reminder_sent_at is not None and date_within_margin(
                case.last_entities_reminder_sent_at, margin
            ):
                continue

            last_action_date = case.last_action_at
            if last_action_date is not None:
                # there was a status change
                if not date_within_margin(last_action_date, margin):
                    # and there was no status update for at least $margin time
                    case.send_entities_reminder()
                    emails_sent += 1
        return emails_sent
