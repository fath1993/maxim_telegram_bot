from django.core.management.base import BaseCommand
from custom_logs.models import CustomLog


def clear_data():
    custom_logs = CustomLog.objects.filter()
    custom_logs.delete()


class Command(BaseCommand):
    def handle(self, *args, **options):
        clear_data()
