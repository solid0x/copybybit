from django.apps import AppConfig
from django.core.cache import cache


class DashboardConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'dashboard'

    def ready(self):
        cache.clear()
