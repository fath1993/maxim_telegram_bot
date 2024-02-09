import threading
import time
import uuid
from django.db.models import Q

from accounts.models import UserRequestHistory
from core.models import File, get_core_settings
from custom_logs.models import custom_log
from envato.enva_defs import check_if_sign_in_is_needed, envato_download_file
from envato.models import get_envato_config_settings, EnvatoAccount


class EnvatoScraperMainFunctionThread(threading.Thread):
    def __init__(self, name):
        super().__init__()
        self._name = name

    def run(self):
        custom_log("EnvatoScraperMainFunctionThread: start thread", "d")
        while True:
            if get_core_settings().envato_scraper_is_active:
                try:
                    custom_log("envato_scraper_main_function: has been started", "d")
                    envato_scraper_main_function()
                    custom_log("envato_scraper_main_function: has been finished. waiting for 5 seconds", "d")
                except Exception as e:
                    custom_log(f"envato_scraper_main_function: try/except-> err: {str(e)}. waiting for 5 seconds", "d")
            else:
                custom_log(f"envato_scraper_main_function: core settings-> envato scraper is active? no. waiting for 5 seconds", "d")
            time.sleep(5)


def envato_scraper_main_function():
    active_threads = threading.enumerate()
    desired_threads_name = []
    for thread in active_threads:
        # custom_log(f"Thread name: {thread.name}, Thread ID: {thread.ident}, Is alive: {thread.is_alive()}")
        if thread.is_alive():
            if str(thread.name).find("en_th_") != -1:  # en_th_ means: envato_threads_
                desired_threads_name.append(thread.name)

    if len(desired_threads_name) < get_envato_config_settings().envato_thread_number:
        custom_log("envato_scraper_main_function: there is no file to download. we are waiting for 5 seconds", "d")
        user_requests_history = UserRequestHistory.objects.filter(has_finished=False)
        envato_files = []
        for user_request_history in user_requests_history:
            en_files = user_request_history.files.all()
            for en_file in en_files:
                if en_file.file_type == 'envato' and en_file.file == '' and not en_file.in_progress and en_file.is_acceptable_file:
                    envato_files.append(en_file)
        envato_files = envato_files[:get_envato_config_settings().envato_queue_number]
        if len(envato_files) > 0:
            try:
                envato_accounts = EnvatoAccount.objects.filter(is_account_active=True)
                if envato_accounts.count() != 0:
                    envato_account = envato_accounts.latest('id')
                else:
                    raise
                for en_item in envato_files:
                    if en_item.file_storage_link:
                        continue
                    else:
                        sign_in_required = check_if_sign_in_is_needed(envato_account)
                        if sign_in_required:
                            raise
                        break
                for file in envato_files:
                    file.in_progress = True
                    file.save()
                EnvatoDownloadFileHandlerThread(envato_files=envato_files, name=f"en_th_{str(uuid.uuid4())}",
                                                account_to_use=envato_account).start()
            except:
                custom_log(
                    "envato_scraper_main_function: the account is not working. pls insert active account or run auth function. we are waiting for 5 seconds",
                    "d")
                time.sleep(5)
        else:
            custom_log("envato_scraper_main_function: there is no file to download. we are waiting for 5 seconds",
                       "d")
    else:
        custom_log(
            f"envato_scraper_main_function->maximum active thread has reached: {len(desired_threads_name)}/{get_envato_config_settings().envato_thread_number}. we are waiting for 5 seconds",
            "d")
    time.sleep(5)


class EnvatoDownloadFileHandlerThread(threading.Thread):
    def __init__(self, envato_files, account_to_use, name):
        super().__init__()
        self._name = name
        self.envato_files = envato_files
        self.account_to_use = account_to_use

    def run(self):
        custom_log(f"EnvatoDownloadFileHandlerThread: {self.name} thread has been started", "d")
        try:
            custom_log("envato_download_file: has been started", "d")
            envato_download_file(self.envato_files, self.account_to_use)
            custom_log("envato_download_file: has been finished", "d")
            custom_log(f"EnvatoDownloadFileHandlerThread: {self.name} thread has been finished", "d")
        except Exception as e:
            for file in self.envato_files:
                file.in_progress = False
                file.is_acceptable_file = False
                file.save()
            custom_log(f"envato_download_file: try/except. err: {str(e)}", "d")
        return