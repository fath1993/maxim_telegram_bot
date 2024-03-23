import time

from django.core.management import BaseCommand

from core.tasks import task_test_1, task_test_2, task_test_3
from custom_logs.models import custom_log

from celery import current_app
from celery import shared_task
from celery.result import AsyncResult


class Command(BaseCommand):
    def handle(self, *args, **options):
        file_page_link = input()
        if file_page_link.find('https://motionarray.com/') != -1:
            file_page_link = str(file_page_link)
            if file_page_link.find('/?q=') != -1:
                file_page_link = file_page_link.split('?q=')[0]
            if file_page_link[-1] == '/':
                file_page_link = file_page_link[:-1]
            file_page_link = file_page_link.split('-')
            unique_code = file_page_link[-1]
            file_page_link = '-'.join(file_page_link)
            file_page_link = f'{file_page_link}/'
            print(unique_code)
            print(file_page_link)


def task_exists(task_name):
    registered_tasks = current_app.tasks.keys()
    for task_name in registered_tasks:
        custom_log(task_name)
    return task_name in registered_tasks


def task_exists_all():
    task_names = ['task_test_1', 'task_test_2', 'task_test_3']
    task_test_1.delay()
    task_test_2.delay()
    task_test_3.delay()
    time.sleep(3)
    task_statuses = {}
    for task_name in task_names:
        task_result = AsyncResult(task_name)
        task_statuses[task_name] = task_result.status
    print(f'task_statuses: {task_statuses}')
    time.sleep(1)
    task_statuses = {}
    for task_name in task_names:
        task_result = AsyncResult(task_name)
        task_statuses[task_name] = task_result.status
    print(f'task_statuses: {task_statuses}')
    time.sleep(1)
    task_statuses = {}
    for task_name in task_names:
        task_result = AsyncResult(task_name)
        task_statuses[task_name] = task_result.status
    print(f'task_statuses: {task_statuses}')
    time.sleep(5)
    task_statuses = {}
    for task_name in task_names:
        task_result = AsyncResult(task_name)
        task_statuses[task_name] = task_result.status
    print(f'task_statuses: {task_statuses}')


def core_crontab_task():
    # Get the inspect instance
    inspector = current_app.control.inspect()

    # Get list of active tasks
    active_tasks = inspector.active()
    custom_log(f'active_tasks: {active_tasks}')

    # Get list of scheduled tasks
    scheduled_tasks = inspector.scheduled()
    custom_log(f'scheduled_tasks: {scheduled_tasks}')

    # Get list of reserved tasks (i.e., tasks currently being executed)
    reserved_tasks = inspector.reserved()
    custom_log(f'reserved_tasks: {reserved_tasks}')

    if not task_exists(task_name='task_test_1'):
        task_test_1.delay()
        custom_log(f'task 1 started')
    else:
        custom_log(f'task 1 already exists')
    if not task_exists(task_name='task_test_2'):
        task_test_2.delay()
        custom_log(f'task 2 started')
    else:
        custom_log(f'task 2 already exists')
    if not task_exists(task_name='task_test_3'):
        task_test_3.delay()
        custom_log(f'task 3 started')
    else:
        custom_log(f'task 3 already exists')

