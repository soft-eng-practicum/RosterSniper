from django.apps import AppConfig


class RSConfig(AppConfig):
    name = 'core'

    def ready(self):
        import core.signals
