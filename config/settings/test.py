"""
With these settings, tests run faster.
"""

from .base import *  # noqa
from .base import env

# GENERAL
# https://docs.djangoproject.com/en/dev/ref/settings/#secret-key
SECRET_KEY = env(
    "DJANGO_SECRET_KEY",
    default="OjllrghggDgzecZprHLeVfKXc3xo9317AVjZljk2j1G0dlx7jmphqw7MDiVCoMlk",
)
# https://docs.djangoproject.com/en/dev/ref/settings/#test-runner
TEST_RUNNER = "django.test.runner.DiscoverRunner"

# CACHES
# https://docs.djangoproject.com/en/dev/ref/settings/#caches
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "",
    }
}

# CELERY
# Emulate celery behavior to make view tests work.
CELERY_TASK_ALWAYS_EAGER = True
CELERY_TASK_EAGER_PROPAGATES = True

# DATABASE
# 4.3 Disable Database Serialization, Page 50, Speed up your Django Tests, Adam Johnson
DATABASES["default"]["TEST"] = {"SERIALIZE": False}

# PASSWORDS
# https://docs.djangoproject.com/en/dev/ref/settings/#password-hashers
PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]

# TEMPLATES
TEMPLATES[-1]["OPTIONS"]["loaders"] = [  # type: ignore[index] # noqa F405
    (
        "django.template.loaders.cached.Loader",
        [
            "django.template.loaders.filesystem.Loader",
            "django.template.loaders.app_directories.Loader",
        ],
    )
]

# https://github.com/nedbat/django_coverage_plugin/issues/18#issuecomment-430370581
TEMPLATES[-1]["OPTIONS"]["debug"] = True  # type: ignore[index] # noqa F405

# EMAIL
# https://docs.djangoproject.com/en/dev/ref/settings/#email-backend
EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"

# Remove throttle to make tests /w freezgun work: https://github.com/spulec/freezegun/issues/382
# django-rest-framework - https://www.django-rest-framework.org/api-guide/settings/
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework.authentication.SessionAuthentication",
        "rest_framework.authentication.TokenAuthentication",
    ),
}
