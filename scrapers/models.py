import random
from django.db import models
from django_jalali.db import models as jmodel


class EnvatoSetting(models.Model):
    sleep_time = models.PositiveSmallIntegerField(default=5, verbose_name="زمان توقف ربات بین هر کوئری")

    def __str__(self):
        return 'تنظیمات انواتو'

    class Meta:
        verbose_name = 'تنظیمات انواتو'
        verbose_name_plural = 'تنظیمات انواتو'


def get_envato_config_settings():
    try:
        envato_config_settings = EnvatoSetting.objects.filter().latest('id')
    except:
        envato_config_settings = EnvatoSetting(
            sleep_time=5,
        )
        envato_config_settings.save()
    return envato_config_settings


class EnvatoAccount(models.Model):
    envato_user = models.CharField(max_length=255, null=True, blank=True, verbose_name='نام کاربری انواتو')
    envato_pass = models.CharField(max_length=255, null=True, blank=True, verbose_name='کلمه عبور انواتو')
    envato_cookie = models.FileField(upload_to='envato/cookies', null=True, blank=True, verbose_name='کوکی انواتو')
    envato_account_description = models.TextField(null=True, blank=True, verbose_name='توضیحات')
    limited_date = jmodel.jDateTimeField(null=True, blank=True, verbose_name='تاریخ و زمان لیمیت')
    is_account_active = models.BooleanField(default=True, verbose_name='آیا اکانت فعال است؟')

    number_of_daily_usage = models.PositiveSmallIntegerField(default=0, null=False, blank=False, editable=False, verbose_name='تعداد استفاده طی اخرین روز')
    daily_bandwidth_usage = models.FloatField(default=0, null=False, blank=False, editable=False, verbose_name='پهنای باند استفاده طی اخرین روز')

    def __str__(self):
        return self.envato_user + ' : ' + self.envato_pass

    class Meta:
        ordering = ['id', ]
        verbose_name = 'اکانت انواتو'
        verbose_name_plural = 'اکانت های انواتو'


def get_envato_account():
    envato_accounts = EnvatoAccount.objects.filter(is_account_active=True)
    number_of_accounts = envato_accounts.count()
    if number_of_accounts == 0:
        return None
    else:
        return envato_accounts[random.randint(0, number_of_accounts - 1)]



class MotionArraySetting(models.Model):
    sleep_time = models.PositiveSmallIntegerField(default=5, verbose_name="زمان توقف ربات بین هر کوئری")

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
    motion_array_account_description = models.TextField(null=True, blank=True, verbose_name='توضیحات')
    limited_date = jmodel.jDateTimeField(null=True, blank=True, verbose_name='تاریخ و زمان لیمیت')
    is_account_active = models.BooleanField(default=True, verbose_name='آیا اکانت فعال است؟')

    number_of_daily_usage = models.PositiveSmallIntegerField(default=0, null=False, blank=False, editable=False, verbose_name='تعداد استفاده طی اخرین روز')
    daily_bandwidth_usage = models.FloatField(default=0, null=False, blank=False, editable=False,
                                              verbose_name='پهنای باند استفاده طی اخرین روز')

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