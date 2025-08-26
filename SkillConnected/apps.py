from django.apps import AppConfig


class SkillconnectedConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'SkillConnected'

    def ready(self):
        import SkillConnected.signals







