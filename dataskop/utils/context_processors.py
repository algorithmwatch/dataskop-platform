from django.conf import settings
from django.contrib.sites.models import Site


def settings_context(_request):
    """
    Settings available by default to the templates context.

    Note: we intentionally do NOT expose the entire settings
    to prevent accidental leaking of sensitive information.
    """
    return {
        "DEBUG": settings.DEBUG,
        # add site because when sending emails, we don't have access to `request`
        "current_site": Site.objects.get_current(),
    }
