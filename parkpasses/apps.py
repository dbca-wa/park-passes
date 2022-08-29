from django.apps import AppConfig
from django.conf import settings


class ParkPassesConfig(AppConfig):
    name = "parkpasses"
    verbose_name = settings.SYSTEM_NAME

    run_once = False

    def ready(self):
        if not self.run_once:
            from parkpasses.components.users import signals  # noqa: F401

        self.run_once = True
