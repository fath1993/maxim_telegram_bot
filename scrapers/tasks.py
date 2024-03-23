import threading
import time
import uuid
from accounts.models import UserRequestHistory
from core.models import get_core_settings
from custom_logs.models import custom_log
from scrapers.defs_envato import EnvatoAccount, envato_download_file, \
    envato_check_if_sign_in_is_needed
from scrapers.defs_motionarray import motion_array_download_file, motion_array_check_if_sign_in_is_needed
from scrapers.models import MotionArrayAccount


class ScrapersMainFunctionThread(threading.Thread):
    def __init__(self, name):
        super().__init__()
        self._name = name

    def run(self):
        custom_log("ScrapersMainFunctionThread: start thread", "d")
        while True:
            try:
                custom_log("scrapers_main_function: has been started", "d")
                scrapers_main_function()
                custom_log("scrapers_main_function: has been finished. waiting for 5 seconds", "d")
            except Exception as e:
                custom_log(f"scrapers_main_function: try/except-> err: {str(e)}. waiting for 5 seconds", "d")
            time.sleep(5)


def scrapers_main_function():
    active_threads = threading.enumerate()
    desired_threads_name = []
    for thread in active_threads:
        # custom_log(f"Thread name: {thread.name}, Thread ID: {thread.ident}, Is alive: {thread.is_alive()}")
        if thread.is_alive():
            if str(thread.name).find("en_th_") != -1:  # en_th_ means: envato_threads_
                desired_threads_name.append(thread.name)

    if len(desired_threads_name) < get_core_settings().thread_number:
        custom_log("scrapers_main_function: there is no file to download. we are waiting for 5 seconds", "d")
        user_requests_history = UserRequestHistory.objects.filter(has_finished=False)
        processing_files = []
        for user_request_history in user_requests_history:
            requested_files = user_request_history.files.all()
            for requested_file in requested_files:
                if requested_file.file == '' and not requested_file.in_progress and requested_file.is_acceptable_file:
                    processing_files.append(requested_file)
        processing_files = processing_files[:get_core_settings().queue_number]
        if len(processing_files) > 0:
            for processing_file in processing_files:
                if processing_file.file_storage_link:
                    continue
                else:
                    try:
                        if processing_file.file_type == 'envato':
                            while True:
                                envato_accounts = EnvatoAccount.objects.filter(is_account_active=True,
                                                                               envato_account_total_daily_limit__lte=get_core_settings().envato_account_total_daily_limit).order_by(
                                    'number_of_daily_usage')
                                if envato_accounts.count() == 0:
                                    custom_log(
                                        "scrapers_main_function: there is no envato active account. pls insert active envato account.")
                                    break
                                first_account = envato_accounts.first()
                                sign_in_required = envato_check_if_sign_in_is_needed(first_account)
                                if sign_in_required:
                                    first_account.is_account_active = False
                                    first_account.save()
                                    time.sleep(0.05)
                                else:
                                    processing_file.in_progress = True
                                    processing_file.save()
                                    DownloadFileHandlerThread(file=processing_file, name=f"en_th_{str(uuid.uuid4())}",
                                                              account_to_use=first_account).start()
                                    break
                        elif processing_file.file_type == 'MotionArray':
                            motion_array_accounts = MotionArrayAccount.objects.filter(is_account_active=True,
                                                                                      motion_array_account_total_daily_limit=get_core_settings().motion_array_account_total_daily_limit).order_by(
                                'number_of_daily_usage').first()

                            if motion_array_accounts.count() == 0:
                                custom_log(
                                    "scrapers_main_function: there is no motion array active account. pls insert active envato account.")
                                break
                            first_account = motion_array_accounts.first()
                            sign_in_required = motion_array_check_if_sign_in_is_needed(first_account)
                            if sign_in_required:
                                first_account.is_account_active = False
                                first_account.save()
                                time.sleep(0.05)
                            else:
                                processing_file.in_progress = True
                                processing_file.save()
                                DownloadFileHandlerThread(file=processing_file, name=f"ma_th_{str(uuid.uuid4())}",
                                                          account_to_use=first_account).start()
                                break
                        else:
                            pass
                    except Exception as e:
                        custom_log(
                            "scrapers_main_function: the account is not working. pls insert active account or run auth function. we are waiting for 5 seconds")
        else:
            custom_log("scrapers_main_function: there is no file to download. we are waiting for 5 seconds",
                       "d")
    else:
        custom_log(
            f"scrapers_main_function->maximum active thread has reached: {len(desired_threads_name)}/{get_core_settings().thread_number}. we are waiting for 5 seconds",
            "d")
    time.sleep(5)


class DownloadFileHandlerThread(threading.Thread):
    def __init__(self, file, account_to_use, name):
        super().__init__()
        self._name = name
        self.file = file
        self.account_to_use = account_to_use

    def run(self):
        custom_log(f"DownloadFileHandlerThread: {self.name} thread has been started")
        try:
            if self.file.file_type == 'envato':
                custom_log("envato_download_file function has been started")
                envato_download_file(self.file, self.account_to_use)
                custom_log("envato_download_file function has been finished")
            elif self.file.file_type == 'MotionArray':
                custom_log("motion_array_download_file function has been started")
                motion_array_download_file(self.file, self.account_to_use)
                custom_log("motion_array_download_file function has been finished")
            else:
                pass
        except Exception as e:
            custom_log(f"envato_download_file: try/except. err: {str(e)}", "d")
            self.file.in_progress = False
            self.file.is_acceptable_file = False
            self.file.save()
        custom_log(f"EnvatoDownloadFileHandlerThread: {self.name} thread has been finished")

