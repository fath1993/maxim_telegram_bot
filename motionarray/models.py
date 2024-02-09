import random
from django.db import models
from django_jalali.db import models as jmodel


class MotionArraySetting(models.Model):
    sleep_time = models.PositiveSmallIntegerField(default=5, verbose_name="زمان توقف ربات بین هر کوئری")
    motion_array_thread_number = models.PositiveSmallIntegerField(default=4, null=False, blank=False, verbose_name='تعداد پردازش همزمان موشن ارای')
    motion_array_queue_number = models.PositiveSmallIntegerField(default=4, null=False, blank=False, verbose_name='تعداد پردازش صف موشن ارای')

    def __str__(self):
        return 'تنظیمات موشن ارای'

    class Meta:
        verbose_name = 'تنظیمات موشن ارای'
        verbose_name_plural = 'تنظیمات موشن ارای'


def get_motion_array_config_settings():
    try:
        motion_array_config_settings = MotionArraySetting.objects.filter().latest('id')
    except:
        motion_array_config_settings = MotionArraySetting(
            sleep_time=5,
        )
        motion_array_config_settings.save()
    return motion_array_config_settings


class MotionArrayAccount(models.Model):
    motion_array_user = models.CharField(max_length=255, null=True, blank=True, verbose_name='نام کاربری موشن ارای')
    motion_array_pass = models.CharField(max_length=255, null=True, blank=True, verbose_name='کلمه عبور موشن ارای')
    motion_array_cookie = models.FileField(upload_to='motion-array/cookies', null=True, blank=True, verbose_name='کوکی موشن ارای')
    motion_array_account_description = models.CharField(max_length=255, null=True, blank=True, verbose_name='توضیحات')
    limited_date = jmodel.jDateTimeField(null=True, blank=True, verbose_name='تاریخ و زمان لیمیت')
    is_account_active = models.BooleanField(default=True, verbose_name='آیا اکانت فعال است؟')


    def __str__(self):
        return self.motion_array_user + ' : ' + self.motion_array_pass

    class Meta:
        ordering = ['id', ]
        verbose_name = 'اکانت موشن ارای'
        verbose_name_plural = 'اکانت های موشن ارای'



def get_motion_array_account():
    motion_array_accounts = MotionArrayAccount.objects.filter(is_account_active=True)
    number_of_accounts = motion_array_accounts.count()
    if number_of_accounts == 0:
        return None
    else:
        return motion_array_accounts[random.randint(0, number_of_accounts - 1)]
