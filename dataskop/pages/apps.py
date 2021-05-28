from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class PagesConfig(AppConfig):
    name = "dataskop.pages"
    verbose_name = _("pages")

    def ready(self):
        try:
            import dataskop.pages.signals  # noqa F401
        except ImportError:
            pass
