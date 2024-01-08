import json
import os
import random
import threading
import time

import jdatetime
from django.contrib.auth.models import User
from django.http import HttpResponse

from accounts.models import UserRequestHistory, SingleToken, UserFileHistory
from core.models import File, LinkText
from custom_logs.models import custom_log
from envato.tasks import EnvatoScraperMainFunctionThread
from maxim_telegram_bot.settings import BASE_DIR, BASE_URL
from utilities.percentage_visual import percentage_visual
from utilities.telegram_message_handler import telegram_http_update_message_via_post_method, \
    telegram_http_send_message_via_post_method


class ScrapersMainFunctionThread(threading.Thread):
    def __init__(self, name):
        super().__init__()
        self._name = name

    def run(self):
        active_threads = threading.enumerate()
        threads_name_list = []
        for thread in active_threads:
            if thread.is_alive():
                threads_name_list.append(str(thread.name))
        custom_log(threads_name_list)
        if not 'general_functions_thread' in threads_name_list:
            custom_log("general_functions: start GeneralFunctionsThread", "d")
            GeneralFunctionsThread(name='general_functions_thread').start()
            time.sleep(1)
        if not 'envato_scraper_main_function_thread' in threads_name_list:
            custom_log("general_functions: start EnvatoScraperMainFunctionThread", "d")
            EnvatoScraperMainFunctionThread(name='envato_scraper_main_function_thread').start()
            time.sleep(1)


class GeneralFunctionsThread(threading.Thread):
    def __init__(self, name):
        super().__init__()
        self._name = name

    def run(self):
        active_threads = threading.enumerate()
        threads_name_list = []
        for thread in active_threads:
            if thread.is_alive():
                threads_name_list.append(str(thread.name))
        if not 'repeat_after_failed_thread' in threads_name_list:
            custom_log("general_functions: start RepeatAfterFailedThread", "d")
            RepeatAfterFailedThread(name='repeat_after_failed_thread').start()
            time.sleep(1)
        if not 'user_download_history_observer_thread' in threads_name_list:
            custom_log("general_functions: start UserDownloadHistoryObserverThread", "d")
            UserDownloadHistoryObserverThread(name='user_download_history_observer_thread').start()
            time.sleep(1)
        if not 'media_folder_cleaner_thread' in threads_name_list:
            custom_log("general_functions: start MediaFolderCleanerThread", "d")
            MediaFolderCleanerThread(name='media_folder_cleaner_thread').start()
            time.sleep(1)
        if not 'reset_daily_limit_thread' in threads_name_list:
            custom_log("general_functions: start ResetDailyLimitThread", "d")
            ResetDailyLimitThread(name='reset_daily_limit_thread').start()
            time.sleep(1)


class UserDownloadHistoryObserverThread(threading.Thread):
    def __init__(self, name):
        super().__init__()
        self._name = name

    def run(self):
        custom_log("UserDownloadHistoryObserverThread: start thread", "d")
        while True:
            try:
                custom_log("user_download_history_observer: has been started", "d")
                user_download_history_observer()
                custom_log("user_download_history_observer: has been finished.  waiting for 5 seconds", "d")
            except Exception as e:
                custom_log(f"user_download_history_observer:try/except-> err: {str(e)}.  waiting for 5 seconds", "d")
            time.sleep(5)


def user_download_history_observer():
    try:
        user_requests_history = UserRequestHistory.objects.filter(has_finished=False)
        for user_request in user_requests_history:
            time.sleep(1)
            has_this_request_finished = True
            for user_file in user_request.files.all():
                if user_file.file == '':
                    if user_file.failed_repeat == 10:
                        pass
                    else:
                        has_this_request_finished = False
                else:
                    pass
            user_request.has_finished = has_this_request_finished
            user_request.save()
            data_track = json.loads(user_request.data_track)
            all_links = []
            if has_this_request_finished:
                try:
                    text = f'''دانلود موارد درخواستی شما تکمیل و به شرح زیر می باشد: \n\n'''
                    unapproved_files_response = []
                    for file in user_request.files.all().order_by('-created_at'):
                        if file.file:
                            text += f'سرویس دهنده: EnvatoElement'
                            text += f'\n'
                            text += f'کد 🔁: {file.unique_code}'
                            text += f'\n'
                            text += f'<a href="{BASE_URL}{file.file.url}">لینک دانلود</a>'
                            all_links.append(f'{BASE_URL}{file.file.url}')
                            text += f'\n'
                            text += f'____________________'
                            text += f'\n\n'
                            new_user_file_history = UserFileHistory.objects.create(user=user_request.user, media=file)
                        else:
                            unapproved_files_response.append(file)
                            text += f'سرویس دهنده: EnvatoElement'
                            text += f'\n'
                            text += f'کد 🔁: {file.unique_code}'
                            text += f'\n'
                            text += f'<b>مشکل در دانلود</b>'
                            text += f'\n'
                            text += f'____________________'
                            text += f'\n\n'
                    if len(all_links) > 1:
                        new_link_text = LinkText.objects.create(
                            link_text_id=random.randint(99999999999999, 9999999999999999),
                            links=json.dumps(all_links)
                        )
                        download_url = f"{BASE_URL}core/merge-and-download&id={new_link_text.link_text_id}"
                        text += f'<a href="{download_url}">جهت دریافت تمامی لینک ها کلیک کنید</a>'
                        text += '\n'
                    telegram_http_update_message_via_post_method(chat_id=user_request.user_request_history_detail.telegram_chat_id,
                                                                 message_id=user_request.user_request_history_detail.telegram_message_id,
                                                                 text=text, parse_mode='HTML')
                    custom_log(f'user_requests_history: a request just finished for user: {user_request.user.username}')
                    time.sleep(1)

                    # return unapproved file response token to user
                    try:
                        profile = user_request.user.user_profile
                        if data_track['just_daily'] == 'true':
                            profile.daily_used_total -= len(unapproved_files_response)
                            profile.multi_token_daily_used -= len(unapproved_files_response)
                        elif data_track['just_single'] == 'true':
                            profile.daily_used_total -= len(unapproved_files_response)
                            i = 0
                            for idx in json.loads(data_track['single_used_tokens_id']):
                                single_token = SingleToken.objects.get(id=idx)
                                single_token.is_used = False
                                single_token.save()
                                i += 1
                                if i == len(unapproved_files_response):
                                    break
                        elif data_track['daily_and_single'] == 'true':
                            profile.daily_used_total -= len(unapproved_files_response)
                            profile.multi_token_daily_used -= int(data_track['daily_used_number'])
                            i = 0
                            for idx in json.loads(data_track['single_used_tokens_id']):
                                single_token = SingleToken.objects.get(id=idx)
                                single_token.is_used = False
                                single_token.save()
                                i += 1
                                if i == abs(len(unapproved_files_response) - int(data_track['daily_used_number'])):
                                    break
                        profile.save()
                        custom_log(f'return unapproved file response toke to user. just {len(unapproved_files_response)} token returned')
                    except Exception as e:
                        custom_log(f'return unapproved file response toke to user. error: {str(e)}')
                    reply_text = f''''''
                    reply_text += f'✅لینک آیتم ها آماده دانلود هستند'
                    reply_text += '\n'
                    reply_text += f'👆لینک دانلود کد های ارسالی در پیام بالا می باشند'
                    reply_text += '\n'
                    if len(unapproved_files_response) != 0:
                        reply_text += f'دانلود {len(unapproved_files_response)} فایل ناموفق و اعتبار کسر شده عودت داده شد'
                        reply_text += '\n\n'
                    profile = user_request.user.user_profile
                    if profile.multi_token:
                        if profile.multi_token.expiry_date > jdatetime.datetime.now():
                            reply_text += f'🌌بسته دانلود روزانه({profile.multi_token.daily_count} عدد در روز):'
                            reply_text += f'\n'
                            reply_text += f'<b>⌛تاریخ انقضا بسته: {profile.multi_token.expiry_date.strftime("%Y/%m/%d %H:%M")}</b>'
                            reply_text += f'\n'
                            reply_text += f'<b>تعداد مصرف شده در 24 ساعت: {profile.multi_token_daily_used} از {profile.multi_token.daily_count}</b>'
                            reply_text += f'\n'
                            reply_text += f'(محدودیت دانلود هر 24 ساعت ریست می شود)'
                            reply_text += f'\n\n'
                    reply_text += f'⭐بسته اعتباری: {profile.single_tokens.filter(is_used=False, expiry_date__gte=jdatetime.datetime.now()).count()} عدد (تاریخ انقضا: ⌛ نامحدود)'
                    reply_text += f'\n\n'
                    telegram_http_send_message_via_post_method(chat_id=user_request.user_request_history_detail.telegram_chat_id,
                                                               reply_to_message_id=user_request.user_request_history_detail.telegram_message_id,
                                                               text=reply_text, parse_mode='HTML')
                    time.sleep(1)
                except Exception as e:
                    custom_log(f'this is the error : {str(e)}')
            else:
                # اضافه کردن تایید فعالیت بر اساس فعال بودن ربات
                text = f'''موارد زیر درحال دریافت از سایت مقصد می باشند:'''
                text += '\n\n'
                for file in user_request.files.all().order_by('-created_at'):
                    percentage_report = percentage_visual(file.download_percentage)

                    if percentage_report == f'■ ■ ■ ■ ■ ■ ■ ■ ■ ■ 100%':
                        if file.file:
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
                            text += f'□ □ □ □ □ □ □ □ □ □ 0%'
                            text += f'\n'
                            text += f'____________________'
                            text += f'\n\n'
                    else:
                        text += f'سرویس دهنده: EnvatoElement'
                        text += f'\n'
                        text += f'کد 🔁: {file.unique_code}'
                        text += f'\n'
                        text += f'{percentage_report}'
                        text += f'\n'
                        text += f'____________________'
                        text += f'\n\n'
                if user_request.files.all().count() > 1:
                    text += f'<b>دریافت تمامی لینک های دانلود با هم( در حال آماده سازی ... )</b>'
                    text += '\n'
                telegram_http_update_message_via_post_method(chat_id=user_request.user_request_history_detail.telegram_chat_id,
                                                             message_id=user_request.user_request_history_detail.telegram_message_id,
                                                             text=text, parse_mode='HTML')
                time.sleep(1)
    except Exception as e:
        custom_log(f'user_download_history_observer exception: error: {str(e)}')
        time.sleep(5)


class RepeatAfterFailedThread(threading.Thread):
    def __init__(self, name):
        super().__init__()
        self._name = name

    def run(self):
        custom_log(f"RepeatAfterFailedThread: {self.name} thread has been started", "d")
        while True:
            try:
                custom_log("repeat_download_after_failed: has been started", "d")
                repeat_download_after_failed()
                custom_log("repeat_download_after_failed: has been finished. waiting for 5 seconds", "d")
            except Exception as e:
                custom_log(f"repeat_download_after_failed:try/except-> err: {str(e)}. waiting for 5 seconds", "d")
            time.sleep(5)


def repeat_download_after_failed():
    files = File.objects.filter(is_acceptable_file=False, in_progress=False)
    for file in files:
        if file.failed_repeat < 10:
            file.is_acceptable_file = True
            file.failed_repeat = file.failed_repeat + 1
            file.save()


class MediaFolderCleanerThread(threading.Thread):
    def __init__(self, name):
        super().__init__()
        self._name = name

    def run(self):
        custom_log(f"MediaFolderCleanerThread: {self.name} thread has been started", "d")
        while True:
            try:
                custom_log("clear_download_folder: has been started", "d")
                clear_download_folder()
                custom_log("clear_download_folder: has been finished. waiting fo 60 seconds", "d")
            except Exception as e:
                custom_log(f"clear_download_folder:try/except-> err: {str(e)}. waiting fo 60 seconds", "d")
            time.sleep(60)


def clear_download_folder():
    all_files = File.objects.filter()
    for file in all_files:
        try:
            now = jdatetime.datetime.now()
            file_updated_at = file.updated_at
            difference = now - file_updated_at
            difference_in_seconds = difference.total_seconds()
            if (difference_in_seconds / 3600) > 24:
                file.file = None
                file.save()
        except Exception as e:
            print(f'exception 2: {str(e)}')

    address_list = [f'{BASE_DIR}/media/files', f'{BASE_DIR}/media/envato/files']
    i = 0
    while True:
        for (root, dirs, files) in os.walk(address_list[i], topdown=True):
            for s_file in files:
                print(s_file)
                file_name, file_extension = os.path.splitext(s_file)
                file_modification_time = os.path.getmtime(f'{root}/{s_file}')
                current_time = time.time()
                modified_in_hours_ago = int(round(((current_time - file_modification_time) / 3600), 0))
                if modified_in_hours_ago >= 24:
                    try:
                        selected_file = File.objects.get(file=f'/files/{file_name}{file_extension}')
                        print('this file exist in database')
                    except Exception as e:
                        print('this file doesnt exist in database')
                        os.remove(f'{root}/{s_file}')
                print('--------------------------------')
        i += 1
        if i == 2:
            print('finish')
            break


def merge_and_download(request, text_id):
    link_text = LinkText.objects.get(link_text_id=text_id)
    merged_content = '\n'.join(json.loads(link_text.links))
    response = HttpResponse(merged_content, content_type='text/plain')
    response['Content-Disposition'] = 'attachment; filename=merged_links.txt'
    return response


class ResetDailyLimitThread(threading.Thread):
    def __init__(self, name):
        super().__init__()
        self._name = name

    def run(self):
        custom_log(f"ResetDailyLimitThread: {self.name} thread has been started", "d")
        while True:
            try:
                custom_log("reset_daily_limit_thread: has been started", "d")
                reset_daily_limit()
                custom_log("reset_daily_limit_thread: has been finished. waiting for 5 seconds", "d")
            except Exception as e:
                custom_log(f"reset_daily_limit_thread:try/except-> err: {str(e)}. waiting for 5 seconds", "d")
            time.sleep(3600)


def reset_daily_limit():
    today = jdatetime.datetime.now()
    if today.hour == 1:
        users = User.objects.filter()
        for user in users:
            profile = user.user_profile
            profile.daily_used_total = 0
            profile.multi_token_daily_used = 0
            profile.save()