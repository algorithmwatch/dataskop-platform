from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class CampaignsConfig(AppConfig):
    name = "dataskop.campaigns"
    verbose_name = _("campaigns")

    def ready(self):
        try:
            import dataskop.users.signals  # noqa F401
        except ImportError:
            pass
