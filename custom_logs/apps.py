from django.apps import AppConfig


class CustomLogsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'custom_logs'
    verbose_name = "لاگ"
    verbose_name_plural = "لاگ ها"
