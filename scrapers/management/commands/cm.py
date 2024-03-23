import os
import time

from django.core.management import BaseCommand

from accounts.models import UserRequestHistory
from envato.enva_def import envato_check_auth
from envato.models import EnvatoFile
from maxim_telegram_bot.settings import BASE_DIR, BASE_URL
from utilities.percentage_visual import percentage_visual
from utilities.telegram_message_handler import telegram_http_update_message_via_post_method


class Command(BaseCommand):
    def handle(self, *args, **options):
        envato_check_auth()


def clear_download_folder():
    for (root, dirs, files) in os.walk('/var/www/envato_telegram_bot/media/envato/files', topdown=True):
        for file in files:
            file_name, file_extension = os.path.splitext(file)
            print(file_name)
            print(file_extension)
            file_modification_time = os.path.getmtime(f'{root}/{file}')
            current_time = time.time()
            modified_in_hours_ago = int(round(((current_time - file_modification_time) / 3600), 0))
            print(modified_in_hours_ago)
            if modified_in_hours_ago >= 0:
                try:
                    envato_file = EnvatoFile.objects.get(file=f'/envato/files/{file_name}{file_extension}')
                    print('this file exist in database')
                except Exception as e:
                    print('this file doesnt exist in database')
                    # os.remove(f'{root}/{file}')
            print('--------------------------------')

    files = EnvatoFile.objects.filter()
    for file in files:
        print(file.file.name)


def user_download_history_observer():
    try:
        user_requests_history = UserRequestHistory.objects.filter(has_finished=False)
        for user_request in user_requests_history:
            has_this_request_finished = True
            for user_file in user_request.envato_files.all():
                if user_file.failed_repeat == 10 and user_file.file.name == '' and not user_file.is_acceptable_file:
                    pass
                elif user_file.file.name != '':
                    pass
                else:
                    has_this_request_finished = False
                    break
            user_request.has_finished = has_this_request_finished
            user_request.save()
            if user_request.has_finished:
                text = f'''موارد درخواستی شما به شرح زیر می باشد: \n\n'''
                for file in user_request.envato_files.all():
                    if file.is_acceptable_file:
                        if file.file.name != '' and file.download_percentage == 100:
                            text += f'سرویس دهنده: EnvatoElement'
                            text += f'\n'
                            text += f'کد 🔁: {file.unique_code}'
                            text += f'\n'
                            text += f'<a href="{BASE_URL}{file.file.url}">لینک دانلود</a>'
                            text += f'\n'
                            text += f'____________________'
                            text += f'\n\n'
                        else:
                            text += f'سرویس دهنده: EnvatoElement'
                            text += f'\n'
                            text += f'کد 🔁: {file.unique_code}'
                            text += f'\n'
                            text += f'{percentage_visual(file.download_percentage)}'
                            text += f'\n'
                            text += f'____________________'
                            text += f'\n\n'
                    else:
                        file.is_acceptable_file = True
                        file.failed_repeat = 0
                        file.save()
                        text += f'سرویس دهنده: EnvatoElement'
                        text += f'\n'
                        text += f'کد 🔁: {file.unique_code}'
                        text += f'\n'
                        text += f'<a href="#">مشکل در دانلود</a>'
                        text += f'\n'
                        text += f'____________________'
                        text += f'\n\n'
                telegram_http_update_message_via_post_method(chat_id=user_request.telegram_chat_id,
                                                             message_id=user_request.telegram_message_id,
                                                             text=text, parse_mode='HTML')
            else:
                text = f'''موارد زیر توسط ربات تایید و درحال دریافت از سایت مقصد می باشند: \n\n'''
                for file in user_request.envato_files:
                    if file.is_acceptable_file:
                        if file.file.name != '' and file.download_percentage == 100:
                            text += f'سرویس دهنده: EnvatoElement'
                            text += f'\n'
                            text += f'کد 🔁: {file.unique_code}'
                            text += f'\n'
                            text += f'<a {BASE_URL}{file.file.url}">لینک دانلود</a>'
                            text += f'\n'
                            text += f'____________________'
                            text += f'\n\n'
                        else:
                            text += f'سرویس دهنده: EnvatoElement'
                            text += f'\n'
                            text += f'کد 🔁: {file.unique_code}'
                            text += f'\n'
                            text += f'{percentage_visual(file.download_percentage)}'
                            text += f'\n'
                            text += f'____________________'
                            text += f'\n\n'
                    else:
                        file.is_acceptable_file = True
                        file.failed_repeat = 0
                        file.save()
                        text += f'سرویس دهنده: EnvatoElement'
                        text += f'\n'
                        text += f'کد 🔁: {file.unique_code}'
                        text += f'\n'
                        text += f'<a href="#">مشکل در دانلود</a>'
                        text += f'\n'
                        text += f'____________________'
                        text += f'\n\n'
                telegram_http_update_message_via_post_method(chat_id=user_request.telegram_chat_id,
                                                             message_id=user_request.telegram_message_id,
                                                             text=text, parse_mode='HTML')
    except Exception as e:
        print(str(e))
        time.sleep(5)