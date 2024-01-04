import os

from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import pre_delete
from django.dispatch import receiver
from django_jalali.db import models as jmodel

# FILE_TYPE = (('envato', 'envato'), ('freepik', 'freepik'), ('shutterstock', 'shutterstock'))
FILE_TYPE = (('envato', 'envato'),)


class CoreSetting(models.Model):
    daily_download_limit = models.PositiveSmallIntegerField(default=50, null=False, blank=False, verbose_name='محدودیت دانلود روزانه')
    envato_scraper_is_active = models.BooleanField(default=True, verbose_name='فعالیت ربات انواتو')
    under_construction = models.BooleanField(default=False, verbose_name='در دست تعمیر')
    error_description = models.TextField(null=True, blank=True, verbose_name='توضیح مشکل')

    def __str__(self):
        return str(self.id)

    class Meta:
        verbose_name = 'تنظیم سرویس'
        verbose_name_plural = 'تنظیمات سرویس'


def get_core_settings():
    try:
        settings = CoreSetting.objects.filter()
        if settings.count() == 0:
            raise 
        elif settings.count() == 1: 
            return settings[0]
        else:    
            settings.delete()
            settings = CoreSetting.objects.create(error_description='تنها یک آبجکت از این تنظیمات مجاز می باشد')
            return settings[0]
    except Exception as e:
        settings = CoreSetting.objects.create()
        return settings

class File(models.Model):
    file_type = models.CharField(default='envato', max_length=255, choices=FILE_TYPE, null=False, blank=False,
                                 verbose_name='نوع فایل')
    page_link = models.CharField(max_length=5000, null=False, blank=False, verbose_name="لینک صفحه اصلی فایل")
    unique_code = models.CharField(max_length=5000, null=True, blank=True, verbose_name="کد یکتا")
    file_storage_link = models.CharField(max_length=3000, null=True, blank=True, verbose_name='لینک فضای ذخیره')
    file = models.FileField(upload_to='files/', null=True, blank=True, verbose_name="فایل", max_length=1500)
    download_percentage = models.PositiveSmallIntegerField(default=0, verbose_name='درصد تکمیل دانلود')
    is_acceptable_file = models.BooleanField(default=True, verbose_name='آیا فایل با فرمت های طراحی شده سازگار است؟')
    in_progress = models.BooleanField(default=False, verbose_name='آیا عملیات دانلود در حال اجراست؟')
    failed_repeat = models.PositiveSmallIntegerField(default=0, null=False, blank=False,
                                                     verbose_name="تعداد تلاش های ناموفق برای دانلود این فایل")
    created_at = jmodel.jDateTimeField(auto_now_add=True, verbose_name="تاریخ و زمان ایجاد")
    updated_at = jmodel.jDateTimeField(auto_now=True, verbose_name="تاریخ و زمان بروزرسانی")

    class Meta:
        ordering = ['-updated_at', ]
        verbose_name = "فایل"
        verbose_name_plural = "فایل ها"

    def __str__(self):
        return f'{self.file_type} | {self.unique_code}'


@receiver(pre_delete, sender=File)
def remove_attached_file(sender, instance, **kwargs):
    try:
        os.remove(instance.file.path)
    except:
        pass


class TelegramBotSetting(models.Model):
    bot_address = models.CharField(max_length=255, null=False, blank=False, verbose_name='آدرس')
    bot_token = models.CharField(max_length=255, null=False, blank=False, verbose_name='توکن')

    def __str__(self):
        return 'تنظیمات ربات تلگرام'

    class Meta:
        verbose_name = 'تنظیمات ربات تلگرام'
        verbose_name_plural = 'تنظیمات ربات تلگرام'


def get_envato_telegram_bot_config_settings():
    try:
        envato_telegram_bot_config_settings = TelegramBotSetting.objects.filter().latest('id')
    except:
        envato_telegram_bot_config_settings = TelegramBotSetting(
            bot_address='',
            bot_token='',
        )
        envato_telegram_bot_config_settings.save()
    return envato_telegram_bot_config_settings


class LinkText(models.Model):
    link_text_id = models.CharField(max_length=255, null=False, blank=False, verbose_name='link text id')
    links = models.TextField(null=False, blank=False, verbose_name='links')

    def __str__(self):
        return self.link_text_id

    class Meta:
        verbose_name = 'لینک تکست'
        verbose_name_plural = 'لینک تکست'


class CustomMessage(models.Model):
    key = models.CharField(max_length=255, null=False, blank=False, verbose_name='کلید')
    message = models.TextField(null=True, blank=True, verbose_name='پیام')

    def __str__(self):
        return self.key

    class Meta:
        verbose_name = 'پیام دلخواه'
        verbose_name_plural = 'پیام های دلخواه'