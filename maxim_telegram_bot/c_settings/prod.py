from maxim_telegram_bot.settings import *

SECRET_KEY = env('SECRET_KEY')

DEBUG = True

ALLOWED_HOSTS = ['localhost', '*', ]

DATABASES['default'] = {
    'ENGINE': 'django.db.backends.postgresql_psycopg2',
    'NAME': 'maxim_dev_telegram_bot_central_db',
    'USER': 'maxim_dev_database_admin',
    'PASSWORD': 'sdHG#54F@V58Ssc',
    'HOST': 'localhost',
    'PORT': '',
}

DATABASES['log_db'] = {
    'ENGINE': 'django.db.backends.postgresql_psycopg2',
    'NAME': 'maxim_dev_telegram_bot_log_db',
    'USER': 'maxim_dev_database_admin',
    'PASSWORD': 'sdHG#54F@V58Ssc',
    'HOST': 'localhost',
    'PORT': '',
}

CRONJOBS = [
    ('*/1 * * * *', 'core.tasks.core_crontab_task',),
]

CELERY_BROKER_URL = 'redis://localhost:6379/0'
CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'
CELERY_CACHE_BACKEND = 'django-cache'
CELERY_BROKER_CONNECTION_RETRY_ON_STARTUP = True

