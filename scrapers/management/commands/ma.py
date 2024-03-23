from django.core.management import BaseCommand

from core.models import File
from scrapers.defs_motionarray import motion_array_check_auth, motion_array_download_file
from scrapers.models import MotionArrayAccount


class Command(BaseCommand):
    def handle(self, *args, **options):
        motion_array_file = File.objects.filter(file_type='MotionArray')[0]
        account_to_use = MotionArrayAccount.objects.filter(is_account_active=True)[0]
        motion_array_download_file(motion_array_file, account_to_use)

