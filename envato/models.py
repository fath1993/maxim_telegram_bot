import random
from django.db import models
from django_jalali.db import models as jmodel


class EnvatoSetting(models.Model):
    sleep_time = models.PositiveSmallIntegerField(default=5, verbose_name="زمان توقف ربات بین هر کوئری")
    envato_thread_number = models.PositiveSmallIntegerField(default=4, null=False, blank=False, verbose_name='تعداد پردازش همزمان انواتو')
    envato_queue_number = models.PositiveSmallIntegerField(default=4, null=False, blank=False, verbose_name='تعداد پردازش صف انواتو')

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
    envato_account_description = models.CharField(max_length=255, null=True, blank=True, verbose_name='توضیحات')
    limited_date = jmodel.jDateTimeField(null=True, blank=True, verbose_name='تاریخ و زمان لیمیت')
    is_account_active = models.BooleanField(default=True, verbose_name='آیا اکانت فعال است؟')


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
