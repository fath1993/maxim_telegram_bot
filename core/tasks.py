import threading
import time

import jdatetime

from core.views import user_download_history_observer, repeat_download_after_failed, clear_download_folder, \
    reset_multi_tokens_daily_limit, disable_expired_multi_tokens, reset_accounts_daily_limit
from custom_logs.models import custom_log


from celery import current_app
from celery import shared_task


@shared_task(name='task_test_1', autostart=True)
def task_test_1():
    custom_log(f'this is task 1. we were auto discovered by celery automatically')
    while True:
        custom_log(f'task 1 waiting for 5 sec.')
        time.sleep(5)
        break
    return


@shared_task(name='task_test_2', autostart=True)
def task_test_2():
    custom_log(f'this is task 2. we were auto discovered by celery automatically')
    while True:
        custom_log(f'task 2 waiting for 5 sec.')
        time.sleep(5)
        break
    return


@shared_task(name='task_test_3', autostart=True)
def task_test_3():
    custom_log(f'this is task 3. we were auto discovered by celery automatically')
    while True:
        custom_log(f'task 3 waiting for 5 sec.')
        time.sleep(5)
        break
    return


def task_exists(task_name):
    registered_tasks = current_app.tasks.keys()
    return task_name in registered_tasks


def core_crontab_task():
    # Get the inspect instance
    inspector = current_app.control.inspect()

    # Get list of active tasks
    active_tasks = inspector.active()
    custom_log(f'{active_tasks}')

    # Get list of scheduled tasks
    scheduled_tasks = inspector.scheduled()
    custom_log(f'{scheduled_tasks}')

    # Get list of reserved tasks (i.e., tasks currently being executed)
    reserved_tasks = inspector.reserved()
    custom_log(f'{reserved_tasks}')

    if not task_exists(task_test_1):
        task_test_1.delay()
        custom_log(f'task 1 started')
    else:
        custom_log(f'task 1 already exists')
    if not task_exists(task_test_2):
        task_test_2.delay()
        custom_log(f'task 2 started')
    else:
        custom_log(f'task 2 already exists')
    if not task_exists(task_test_3):
        task_test_3.delay()
        custom_log(f'task 3 started')
    else:
        custom_log(f'task 3 already exists')


class CoreMainFunctionThread(threading.Thread):
    def __init__(self, name):
        super().__init__()
        self._name = name

    def run(self):
        active_threads = threading.enumerate()
        threads_name_list = []
        for thread in active_threads:
            if thread.is_alive():
                threads_name_list.append(str(thread.name))
        if not 'general_functions_thread' in threads_name_list:
            custom_log("general_functions: start GeneralFunctionsThread")
            GeneralFunctionsThread(name='general_functions_thread').start()
            time.sleep(1)
        return


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
            custom_log("general_functions: start RepeatAfterFailedThread")
            RepeatAfterFailedThread(name='repeat_after_failed_thread').start()
            time.sleep(1)
        if not 'user_download_history_observer_thread' in threads_name_list:
            custom_log("general_functions: start UserDownloadHistoryObserverThread")
            UserDownloadHistoryObserverThread(name='user_download_history_observer_thread').start()
            time.sleep(1)
        if not 'media_folder_cleaner_thread' in threads_name_list:
            custom_log("general_functions: start MediaFolderCleanerThread")
            MediaFolderCleanerThread(name='media_folder_cleaner_thread').start()
            time.sleep(1)
        if not 'reset_daily_limit_thread' in threads_name_list:
            custom_log("general_functions: start ResetDailyLimitThread")
            ResetDailyLimitThread(name='reset_daily_limit_thread').start()
            time.sleep(1)
        if not 'disable_expired_multi_tokens' in threads_name_list:
            custom_log("general_functions: start DisableExpiredMultiTokensThread")
            DisableExpiredMultiTokensThread(name='disable_expired_multi_tokens').start()
            time.sleep(1)


class UserDownloadHistoryObserverThread(threading.Thread):
    def __init__(self, name):
        super().__init__()
        self._name = name

    def run(self):
        custom_log("UserDownloadHistoryObserverThread: start thread")
        while True:
            try:
                custom_log("user_download_history_observer: has been started")
                user_download_history_observer()
                custom_log("user_download_history_observer: has been finished.  waiting for 5 seconds")
            except Exception as e:
                custom_log(f"user_download_history_observer:try/except-> err: {str(e)}.  waiting for 5 seconds")
            time.sleep(5)


class RepeatAfterFailedThread(threading.Thread):
    def __init__(self, name):
        super().__init__()
        self._name = name

    def run(self):
        custom_log(f"RepeatAfterFailedThread: {self.name} thread has been started")
        while True:
            try:
                custom_log("repeat_download_after_failed: has been started")
                repeat_download_after_failed()
                custom_log("repeat_download_after_failed: has been finished. waiting for 5 seconds")
            except Exception as e:
                custom_log(f"repeat_download_after_failed:try/except-> err: {str(e)}. waiting for 5 seconds")
            time.sleep(5)


class MediaFolderCleanerThread(threading.Thread):
    def __init__(self, name):
        super().__init__()
        self._name = name

    def run(self):
        custom_log(f"MediaFolderCleanerThread: {self.name} thread has been started")
        while True:
            try:
                custom_log("clear_download_folder: has been started")
                clear_download_folder()
                custom_log("clear_download_folder: has been finished. waiting fo 60 seconds")
            except Exception as e:
                custom_log(f"clear_download_folder:try/except-> err: {str(e)}. waiting fo 60 seconds")
            time.sleep(60)


class ResetDailyLimitThread(threading.Thread):
    def __init__(self, name):
        super().__init__()
        self._name = name

    def run(self):
        custom_log(f"ResetDailyLimitThread: {self.name} thread has been started")
        while True:
            try:
                custom_log("reset_daily_limit_thread: has been started")
                now = jdatetime.datetime.now()
                if 0 < now.hour < 1:
                    reset_multi_tokens_daily_limit()
                    time.sleep(1)
                    reset_accounts_daily_limit()
                custom_log("reset_daily_limit_thread: has been finished. waiting for 5 seconds")
            except Exception as e:
                custom_log(f"reset_daily_limit_thread:try/except-> err: {str(e)}. waiting for 5 seconds")
            time.sleep(3600)


class DisableExpiredMultiTokensThread(threading.Thread):
    def __init__(self, name):
        super().__init__()
        self._name = name

    def run(self):
        custom_log(f"DisableExpiredMultiTokensThread: {self.name} thread has been started")
        while True:
            try:
                custom_log("disable_expired_multi_tokens: has been started")
                disable_expired_multi_tokens()
                custom_log("disable_expired_multi_tokens: has been finished. waiting for 30 seconds")
            except Exception as e:
                custom_log(f"disable_expired_multi_tokens:try/except-> err: {str(e)}. waiting for 30 seconds")
            time.sleep(30)


