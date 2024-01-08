from django.core.management import BaseCommand
from core.tasks import clear_download_folder


class Command(BaseCommand):
    def handle(self, *args, **options):
        clear_download_folder()


