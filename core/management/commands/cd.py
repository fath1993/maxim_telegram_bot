import os
import time

import jdatetime
from django.core.management import BaseCommand

from core.models import File
from maxim_telegram_bot.settings import BASE_DIR


class Command(BaseCommand):
    def handle(self, *args, **options):
        clear_download_folder()


def clear_download_folder():
    all_files = File.objects.filter()
    for file in all_files:
        try:
            now = jdatetime.datetime.now()
            file_updated_at = file.updated_at
            difference = now - file_updated_at
            difference_in_seconds = difference.total_seconds()
            if (difference_in_seconds / 3600) > 24:
                try:
                    os.remove(f'{BASE_DIR}{file.file.url}')
                    file.file = None
                    file.save()
                except Exception as e:
                    print(f'exception 1: {str(e)}')
                    file.file = None
                    file.save()
        except Exception as e:
            print(f'exception 2: {str(e)}')
    for (root, dirs, files) in os.walk(f'{BASE_DIR}/media/envato/files', topdown=True):
        for s_file in files:
            print(s_file)
            file_name, file_extension = os.path.splitext(s_file)
            file_modification_time = os.path.getmtime(f'{root}/{s_file}')
            current_time = time.time()
            modified_in_hours_ago = int(round(((current_time - file_modification_time) / 3600), 0))
            if modified_in_hours_ago >= 24:
                try:
                    selected_file = File.objects.get(file=f'/envato/files/{file_name}{file_extension}')
                    print('this file exist in database')
                except Exception as e:
                    print('this file doesnt exist in database')
                    os.remove(f'{root}/{s_file}')
            print('--------------------------------')