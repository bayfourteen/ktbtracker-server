from django.apps import AppConfig


class KTBTrackerConfig(AppConfig):
    name = "ktbtracker"

    def ready(self):
        import ktbtracker.signals
