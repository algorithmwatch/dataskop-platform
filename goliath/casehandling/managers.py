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

        def _get_last_action_date(case):
            last_action_date = None
            if case.history.all().count() == 0:
                # there is no history, the object was never updated since creation
                last_action_date = case.created_at
            else:
                # getting the most recent version (in the history)
                prev_case = case.history.first()
                while True:
                    if prev_case is None:
                        # there is no history
                        break
                    if prev_case.status == case.status:
                        # no status changed, go further back
                        last_action_date = prev_case.history_date
                        break
                    # iterate through the all the history item
                    prev_case = prev_case.prev_record
            return last_action_date

        emails_sent = 0
        for case in self.filter(
            status=self.model.Status.WAITING_USER_INPUT,
            sent_reminders__lt=max_reminders,
        ):
            if case.last_reminder_sent_at is not None and date_within_margin(
                case.last_reminder_sent_at, margin
            ):
                continue

            last_action_date = _get_last_action_date(case)
            if last_action_date is not None:
                # there was a status change
                if not date_within_margin(last_action_date, margin):
                    # and there was no status update for at least $margin time
                    case.send_reminder_user()
                    emails_sent += 1
        return emails_sent
