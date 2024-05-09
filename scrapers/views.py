import threading
import time
import uuid

from django.http import JsonResponse

from accounts.models import UserRequestHistory
from core.models import get_core_settings
from custom_logs.models import custom_log
from scrapers.defs_envato import envato_check_auth, envato_check_if_sign_in_is_needed, envato_download_file
from scrapers.defs_motionarray import motion_array_check_auth, motion_array_check_if_sign_in_is_needed, \
    motion_array_download_file
from scrapers.models import EnvatoAccount, MotionArrayAccount


def envato_check_auth_view(request):
    if request.user.is_authenticated and request.user.is_superuser:
        if request.method == 'GET':
            envato_check_auth()
            return JsonResponse({'message': 'envato_auth: envato check auth function has been started'})
        else:
            return JsonResponse({'message': 'not allowed'})
    else:
        return JsonResponse({'message': 'not allowed'})


def motion_array_check_auth_view(request):
    if request.user.is_authenticated and request.user.is_superuser:
        if request.method == 'GET':
            motion_array_check_auth()
            return JsonResponse({'message': 'motion_array_auth: motion array check auth function has been started'})
        else:
            return JsonResponse({'message': 'not allowed'})
    else:
        return JsonResponse({'message': 'not allowed'})


def scrapers_main_function():
    active_threads = threading.enumerate()
    desired_threads_name = []
    for thread in active_threads:
        if thread.is_alive():
            if str(thread.name).find("en_th_") != -1 or str(thread.name).find("ma_th_") != -1:  # en_th_ means: envato_threads_
                desired_threads_name.append(thread.name)

    if len(desired_threads_name) < get_core_settings().thread_number:
        user_requests_history = UserRequestHistory.objects.filter(has_finished=False)
        processing_files = []
        for user_request_history in user_requests_history:
            requested_files = user_request_history.files.all()
            for requested_file in requested_files:
                if not requested_file.file and not requested_file.in_progress and requested_file.is_acceptable_file:
                    processing_files.append(requested_file)
        processing_files = processing_files[:get_core_settings().queue_number]
        if len(processing_files) > 0:
            for processing_file in processing_files:
                if processing_file.file_storage_link:
                    processing_file.in_progress = True
                    processing_file.save()
                    if processing_file.file_type == 'envato':
                        DownloadFileHandlerThread(file=processing_file, name=f"en_th_{str(uuid.uuid4())}").start()
                    elif processing_file.file_type == 'motion_array':
                        DownloadFileHandlerThread(file=processing_file, name=f"ma_th_{str(uuid.uuid4())}").start()
                    else:
                        pass
                else:
                    try:
                        if processing_file.file_type == 'envato':
                            while True:
                                envato_accounts = EnvatoAccount.objects.filter(is_account_active=True,
                                                                               number_of_daily_usage__lte=get_core_settings().envato_account_total_daily_limit).order_by(
                                    'number_of_daily_usage')
                                if envato_accounts.count() == 0:
                                    custom_log("scrapers_main_function: there is no envato active account. pls insert active envato account.", f"scrapers")
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
                                    first_account.number_of_daily_usage += 1
                                    first_account.save()
                                    DownloadFileHandlerThread(file=processing_file, name=f"en_th_{str(uuid.uuid4())}",
                                                              account_to_use=first_account).start()
                                    break
                        elif processing_file.file_type == 'motion_array':
                            motion_array_accounts = MotionArrayAccount.objects.filter(is_account_active=True,
                                                                                      number_of_daily_usage__lte=get_core_settings().motion_array_account_total_daily_limit).order_by(
                                'number_of_daily_usage')

                            if motion_array_accounts.count() == 0:
                                custom_log("scrapers_main_function: there is no motion array active account. pls insert active motion array account.", f"scrapers")
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
                                first_account.number_of_daily_usage += 1
                                first_account.save()
                                DownloadFileHandlerThread(file=processing_file, name=f"ma_th_{str(uuid.uuid4())}",
                                                          account_to_use=first_account).start()
                                break
                        else:
                            pass
                    except Exception as e:
                        custom_log(f"scrapers_main_function: try/except--> err: {e}  . we are waiting for 5 seconds", f"scrapers")
        else:
            custom_log("scrapers_main_function: there is no file to download. we are waiting for 5 seconds", f"scrapers")
    else:
        custom_log(f"scrapers_main_function->maximum active thread has reached: {len(desired_threads_name)}/{get_core_settings().thread_number}. we are waiting for 5 seconds", f"scrapers")
    time.sleep(5)


class DownloadFileHandlerThread(threading.Thread):
    def __init__(self, file, name, account_to_use=None):
        super().__init__()
        self.file = file
        self._name = name
        self.account_to_use = account_to_use

    def run(self):
        custom_log(f"DownloadFileHandlerThread: {self.name} thread has been started", f"scrapers")
        try:
            if self.file.file_type == 'envato':
                custom_log("envato_download_file function has been started", f"scrapers")
                envato_download_file(self.file, self.account_to_use)
                custom_log("envato_download_file function has been finished", f"scrapers")
            elif self.file.file_type == 'motion_array':
                custom_log("motion_array_download_file function has been started", f"scrapers")
                motion_array_download_file(self.file, self.account_to_use)
                custom_log("motion_array_download_file function has been finished", f"scrapers")
            else:
                pass
        except Exception as e:
            custom_log(f"envato_download_file: try/except. err: {str(e)}", f"scrapers")
            self.file.in_progress = False
            self.file.is_acceptable_file = False
            self.file.save()
        custom_log(log_level=f"scrapers", description=f"EnvatoDownloadFileHandlerThread: {self.name} thread has been finished")
