from django.apps import AppConfig


class EnvatoConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'scrapers'
    verbose_name = "Scraper"
    verbose_name_plural = "Scrapers"
