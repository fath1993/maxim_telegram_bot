from maxim_telegram_bot.settings import *

SECRET_KEY = env('SECRET_KEY')

DEBUG = True

ALLOWED_HOSTS = ['localhost', '*', ]

DATABASES['default'] = {
    'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'envato_telegram_bot_central_db',
        'USER': 'envato_database_admin',
        'PASSWORD': '85#fihh58',
        'HOST': 'localhost',
        'PORT': '',
}


DATABASES['log_db'] = {
    'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'envato_telegram_bot_log_db',
        'USER': 'envato_database_admin',
        'PASSWORD': '85#fihh58',
        'HOST': 'localhost',
        'PORT': '',
}


