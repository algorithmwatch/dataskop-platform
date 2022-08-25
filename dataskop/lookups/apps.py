from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class LookupsConfig(AppConfig):
    name = "dataskop.lookups"
    verbose_name = _("Lookups")

    def ready(self):
        try:
            import dataskop.lookups.signals  # noqa F401
        except ImportError:
            pass
