import os

from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import pre_delete
from django.dispatch import receiver
from django_jalali.db import models as jmodel

FILE_TYPE = (('envato', 'envato'), ('MotionArray', 'MotionArray'))
ARIA_CODE_ACCEPTANCE = (('همه به جز', 'همه به جز'), ('فقط موارد مشخص', 'فقط موارد مشخص'))

FILE_FORMAT_COST_FACTOR = (('VIDEO', 'VIDEO'), ('AUDIO', 'AUDIO'), ('IMAGE', 'IMAGE'), ('FILE', 'FILE'))

FILE_QUALITY_COST_FACTOR = (('SD', 'SD'), ('HD', 'HD'), ('FHD', 'FHD'), ('2K', '2K'), ('4K', '4K'), ('8K', '8K'))


class AriaCode(models.Model):
    aria_code = models.PositiveSmallIntegerField(null=False, blank=False, verbose_name='کد کشور')

    def __str__(self):
        return f'{self.aria_code}'

    class Meta:
        verbose_name = 'کد کشور'
        verbose_name_plural = 'کد کشور ها'


class FileFormatCostFactor(models.Model):
    name = models.CharField(max_length=255, choices=FILE_FORMAT_COST_FACTOR, null=False, blank=False,
                            verbose_name='نام')
    cost_factor = models.DecimalField(default=1, max_digits=4, decimal_places=2, null=False, blank=False,
                                      verbose_name='ضریب')

    def __str__(self):
        return f'{self.name} | cost factor: {self.cost_factor}'

    class Meta:
        verbose_name = 'ضریب هزینه فرمت فایل'
        verbose_name_plural = 'ضریب هزینه فرمت فایل ها'


class FileQualityCostFactor(models.Model):
    name = models.CharField(max_length=255, choices=FILE_QUALITY_COST_FACTOR, null=False, blank=False,
                            verbose_name='نام')
    cost_factor = models.DecimalField(default=1, max_digits=4, decimal_places=2, null=False, blank=False,
                                      verbose_name='ضریب')

    def __str__(self):
        return f'{self.name} | cost factor: {self.cost_factor}'

    class Meta:
        verbose_name = 'ضریب هزینه کیفیت فایل'
        verbose_name_plural = 'ضریب هزینه کیفیت فایل ها'


class CoreSetting(models.Model):
    envato_daily_download_limit = models.PositiveSmallIntegerField(default=50, null=False, blank=False,
                                                                   verbose_name='محدودیت دانلود روزانه انواتو')
    envato_scraper_is_active = models.BooleanField(default=True, verbose_name='فعالیت ربات انواتو')
    envato_cost_factor = models.PositiveSmallIntegerField(default=1, null=False, blank=False,
                                                          verbose_name='ضریب هزینه انواتو')

    motion_array_daily_download_limit = models.PositiveSmallIntegerField(default=50, null=False, blank=False,
                                                                         verbose_name='محدودیت دانلود روزانه موشن ارای')
    motion_array_scraper_is_active = models.BooleanField(default=True, verbose_name='فعالیت ربات موشن ارای')
    motion_array_cost_factor = models.PositiveSmallIntegerField(default=1, null=False, blank=False,
                                                                verbose_name='ضریب هزینه موشن ارای')

    service_under_construction = models.BooleanField(default=False, verbose_name='در دست تعمیر کلی سرویس')
    error_description = models.TextField(null=True, blank=True, verbose_name='توضیح مشکل')
    aria_code_acceptance = models.CharField(default='همه به جز', max_length=255, choices=ARIA_CODE_ACCEPTANCE,
                                            null=False, blank=False, verbose_name='نوع پذیرش پیش شماره')
    file_format_cost_factors = models.ManyToManyField(FileFormatCostFactor, blank=True,
                                                      verbose_name='ضرایب هزینه فرمت فایل')
    file_quality_cost_factors = models.ManyToManyField(FileQualityCostFactor, blank=True,
                                                       verbose_name='ضرایب هزینه کیفیت فایل')

    def __str__(self):
        return f'تنظیمات سرویس'

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
    file_meta = models.TextField(null=True, blank=True, verbose_name='مشخصات فایل')
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
