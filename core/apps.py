from django.apps import AppConfig

class coreConfig(AppConfig):
    name = 'core'

    def ready(self):
        from core import scheduler
        scheduler.start()
