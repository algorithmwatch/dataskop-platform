# Celery

We use Celery with Redis as broker:

1. for off-loading some work form a web process to a worker process and
2. to schedule periodical background tasks.

## Periodical tasks

- Remind users to verify their donation(s): dataskop.campaigns.tasks.remind_user_registration: Daily
- Add new newsletter subscriptions to Mailjet: dataskop.mailjetsync.tasks.enqueue_confirmed_emails: Daily or every 4 hours
- Heartbeat to check for some information: dataskop.campaigns.tasks.test_task_email: Daily
- TODO: resend_failed_emails
- TODO: Remove unconfirmed donations after 180 days
- Delete expired celery results: celery.backend_cleanup: Daily
