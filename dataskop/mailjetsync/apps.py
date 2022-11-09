from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class MailjetsyncConfig(AppConfig):
    name = "dataskop.mailjetsync"
    verbose_name = _("Mailjetsync")

    def ready(self):
        try:
            import dataskop.mailjetsync.signals  # noqa F401
        except ImportError:
            pass
