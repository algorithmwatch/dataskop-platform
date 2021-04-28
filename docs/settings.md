# Settings via ENV

## `.postgres`

```bash
POSTGRES_HOST=postgres
POSTGRES_PORT=5432
POSTGRES_DB=goliath
POSTGRES_USER=x
POSTGRES_PASSWORD=x
```

## `.django`

### Local / Development

```
# General
USE_DOCKER=yes
IPYTHONDIR=/app/.ipython
DJANGO_DEBUG=yes
URL_ORIGIN=http://localhost:8000

# Redis
REDIS_URL=redis://redis:6379/0

# Celery
CELERY_BROKER_URL=redis://redis:6379/0

# Flower
CELERY_FLOWER_USER=x
CELERY_FLOWER_PASSWORD=x

# Email
MAILJET_API_KEY=x
MAILJET_SECRET_KEY=x
WEBHOOK_SECRET=xx:xx

# Import data from airtable
AIRTABLE_KEY=xx
AIRTABLE_TABLE=xx
AIRTABLE_NAME=Goliath
```

### Production

```
# General
DJANGO_SETTINGS_MODULE=config.settings.production
DJANGO_SECRET_KEY=
DJANGO_ADMIN_URL=
DJANGO_ALLOWED_HOSTS=.unding.de
URL_ORIGIN=https://unding.de

# Security
# TIP: better off using DNS, however, redirect is OK too
DJANGO_SECURE_SSL_REDIRECT=False

# django-allauth
DJANGO_ACCOUNT_ALLOW_REGISTRATION=True

# Gunicorn
WEB_CONCURRENCY=4

# Redis
REDIS_URL=redis://redis:6379/0

# Celery
# Flower
CELERY_FLOWER_USER=
CELERY_FLOWER_PASSWORD=

# Sentry
SENTRY_DSN=https://

# Email
MAILJET_API_KEY=
MAILJET_SECRET_KEY=
WEBHOOK_SECRET=xx:xx

DEFAULT_EMAIL_DOMAIN=undinge.net
DEFAULT_FROM_EMAIL=noreplay@undinge.net
EMAIL_SUBJECT_PREFIX=[Unding]

# Import Data
AIRTABLE_KEY=
AIRTABLE_TABLE=

CONTACT_EMAIL=unding@algorithmwatch.org
ADMIN_NOTIFICATION_EMAIL=unding@algorithmwatch.org

GPG_PUBLIC_KEY_URL=https://
GPG_KEY_NAME=x@x.org

S3_ACCESS=
S3_SECRET=
S3_ENDPOINT=
S3_BUCKET=
S3_REGION=

GOOGLE_VERIFICATION=
```
