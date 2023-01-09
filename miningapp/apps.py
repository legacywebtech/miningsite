from django.apps import AppConfig


class MiningappConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'miningapp'

    def ready(self):
        import miningapp.signals 
