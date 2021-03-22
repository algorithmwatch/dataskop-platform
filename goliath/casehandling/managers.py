import datetime

from django.db import IntegrityError, models, transaction

from ..utils.time import date_within_margin


class CaseManager(models.Manager):
    def create_case_with_email(self, user, **kwargs):
        # try 20 times to generate unique email for this case and then give up
        # increase the number of digits for each try
        error_count = 0
        while True:
            try:
                # Nest the already atomic transaction to let the database safely fail.
                with transaction.atomic():
                    case = self.create(
                        email=user.gen_case_email(error_count + 1), user=user, **kwargs
                    )
                return case
            except IntegrityError as e:
                if "unique constraint" in e.args[0]:
                    error_count += 1
                    if error_count > 20:
                        raise e

    def remind_users(
        self,
    ):
        """
        Iterate over all case and check if the user should get a reminder.
        Default: remind after 7 days, then remind again after 7 days and stop.
        This is specified in the model of `CaseType`.

        Returns the total number of sent emails.
        """
        emails_sent = 0
        for case in self.filter(
            status=self.model.Status.WAITING_USER_INPUT,
        ):
            max_reminders, margin = (
                case.case_type.user_reminder_max,
                case.case_type.user_reminder_margin,
            )

            if case.sent_user_reminders >= max_reminders:
                continue

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

    def remind_entities(self):
        """
        Iterate over all cases and check if the entities should get a reminder.
        Default: remind after 7 days, then remind again after 7 days and stop.
        This is specified in the model of `CaseType`.

        Returns the total number of sent emails.
        """

        emails_sent = 0
        for case in self.filter(
            status=self.model.Status.WAITING_RESPONSE,
        ):
            max_reminders, margin = (
                case.case_type.entity_reminder_max,
                case.case_type.entity_reminder_margin,
            )

            if case.sent_entities_reminders >= max_reminders:
                continue

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
