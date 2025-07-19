from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class UsersConfig(AppConfig):
    name = "thorpat.apps.users"
    verbose_name = _("Users")

    def ready(self):
        # Import signal handlers
        try:
            import thorpat.apps.users.signals  # noqa F401
        except ImportError:
            pass
