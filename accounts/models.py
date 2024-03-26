import random
import jdatetime
from django.contrib.auth.models import User
from django.urls import reverse
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django_jalali.db import models as jmodel

from core.models import File, get_core_settings

MULTI_TOKEN_TYPE = (('motion_array', 'motion_array'), ('envato', 'envato'))
SCRAPER_REDEEM_TOKEN_TYPE = (('motion_array', 'motion_array'), ('envato', 'envato'))


class Profile(models.Model):
    user = models.OneToOneField(User, related_name='user_profile', on_delete=models.CASCADE, null=False, blank=False,
                                editable=False,
                                verbose_name='کاربر')
    user_telegram_phone_number = models.CharField(max_length=255, null=True, blank=True,
                                                  verbose_name='شماره تماس اکانت تلگرام')

    wallet_credit = models.IntegerField(default=0, null=False, blank=False,
                                                           verbose_name='اعتبار حساب')

    user_latest_requested_files = models.TextField(null=True, blank=True, editable=False,
                                                   verbose_name='آخرین فایل های درخواستی کاربر')
    updated_at = jmodel.jDateTimeField(auto_now=True, verbose_name="تاریخ و زمان بروز رسانی")

    def __str__(self):
        return self.user.username

    class Meta:
        ordering = ['-user__id', ]
        verbose_name = 'پروفایل'
        verbose_name_plural = 'پروفایل ها'

    def get_absolute_url(self):
        return reverse('accounts:profile-with-user-id', kwargs={'user_id': self.id})


@receiver(post_save, sender=User)
def auto_create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


class UserMultiToken(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=False, blank=False, editable=False,
                             verbose_name='کاربر')
    token_type = models.CharField(max_length=255, choices=MULTI_TOKEN_TYPE, default='envato', null=False,
                                  blank=False, editable=False,
                                  verbose_name='نوع توکن')
    # these fields are calculated based on user activity
    latest_usage_date = jmodel.jDateTimeField(auto_now=True, verbose_name="تاریخ اخرین استفاده")
    total_remaining_tokens = models.PositiveIntegerField(null=False, blank=False, editable=False,
                                                         verbose_name='تعداد باقیمانده کل')
    daily_remaining_tokens = models.PositiveIntegerField(null=False, blank=False, editable=False,
                                                         verbose_name='تعداد باقیمانده کل')

    # these fields are static data
    total_tokens = models.PositiveIntegerField(null=False, blank=False, editable=False, verbose_name='تعداد کل')
    daily_allowed_number = models.PositiveIntegerField(null=False, blank=False, editable=False,
                                                       verbose_name='تعداد مجاز روزانه')
    expiry_date = jmodel.jDateTimeField(null=False, blank=False, editable=False, verbose_name="تاریخ و زمان انقضا")
    expiry_days = models.PositiveSmallIntegerField(null=False, blank=False, editable=False, verbose_name="تعداد روز انقضا پس از ردیم شدن")

    disabled = models.BooleanField(default=False, verbose_name='فعال')

    def __str__(self):
        if self.disabled:
            return f'id: {self.id} | used'
        else:
            return f'total_remaining_tokens: {self.total_remaining_tokens} | daily_remaining_tokens: {self.daily_remaining_tokens} | latest_usage_date: {self.latest_usage_date.strftime("%Y/%m/%d")}'

    class Meta:
        ordering = ['id', ]
        verbose_name = 'توکن چند تایی کاربر'
        verbose_name_plural = 'توکن های چند تایی کاربران'


# this function return old_active_exist, new_one_is_used_before, new_one_is_created or new_one_is_not_found_in_db
def create_user_multi_token(user, token_type, new_token_unique_code):
    active_multi_token = UserMultiToken.objects.filter(user=user, token_type=token_type, disabled=False,
                                                       expiry_date__gte=jdatetime.datetime.now())
    if active_multi_token.count() == 0:
        pass
    elif active_multi_token == 1:
        return ['old_active_exist', active_multi_token]
    else:
        for each_active_multi_token in active_multi_token:
            each_active_multi_token.delete()

    try:
        scraper_redeem_code = ScraperRedeemToken.objects.get(token_unique_code=new_token_unique_code)
        if scraper_redeem_code.is_used:
            return ['new_one_is_used_before', new_token_unique_code]
        scraper_redeem_code.is_used = True
        scraper_redeem_code.save()
        new_user_multi_token = UserMultiToken.objects.create(
            user=user,
            token_type=scraper_redeem_code.token_type,
            total_remaining_tokens=scraper_redeem_code.total_tokens,
            daily_remaining_tokens=scraper_redeem_code.daily_allowed_number,
            total_tokens=scraper_redeem_code.total_tokens,
            daily_allowed_number=scraper_redeem_code.daily_allowed_number,
            expiry_date=jdatetime.datetime.now() + jdatetime.timedelta(days=scraper_redeem_code.expiry_days),
            expiry_days=scraper_redeem_code.expiry_days,
        )
        return ['new_one_is_created', new_user_multi_token]
    except:
        return ['new_one_is_not_found_in_db', new_token_unique_code]


def does_user_has_multi_token(user, token_type):
    active_multi_token = UserMultiToken.objects.filter(user=user, token_type=token_type, disabled=False,
                                                       expiry_date__gte=jdatetime.datetime.now())
    if active_multi_token.count() == 0:
        return False
    elif active_multi_token == 1:
        return True
    else:
        for each_active_multi_token in active_multi_token:
            each_active_multi_token.delete()
        return False


class WalletRedeemToken(models.Model):
    token_unique_code = models.CharField(max_length=255, null=False, blank=False, editable=False,
                                         verbose_name='کد یکتا')
    charge_amount = models.DecimalField(default=1.00, max_digits=10, decimal_places=2, null=False, blank=False,
                                        verbose_name='مقدار شارژ')
    created_at = jmodel.jDateTimeField(auto_now_add=True, verbose_name="تاریخ و زمان ایجاد")

    is_used = models.BooleanField(default=False, verbose_name='استفاده شده')

    def __str__(self):
        return f'{self.token_unique_code} | amount: {self.charge_amount}'

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'ردیم توکن شارژ حساب'
        verbose_name_plural = 'ردیم توکن های شارژ حساب'

    def save(self, *args, **kwargs):
        if not self.token_unique_code:
            self.token_unique_code = token_generator('wallet')
        super().save(*args, **kwargs)


def user_wallet_charge(user, token_unique_code):
    try:
        wallet_redeem_token = WalletRedeemToken.objects.get(token_unique_code=token_unique_code, is_used=False)
        wallet_redeem_token.is_used = True
        wallet_redeem_token.save()
        profile = user.user_profile
        profile.wallet_permanent_balance += wallet_redeem_token.charge_amount
        profile.save()
        return True
    except:
        return False


class ScraperRedeemToken(models.Model):
    token_name = models.CharField(max_length=255, null=True, blank=True, verbose_name='نام توکن')
    token_type = models.CharField(max_length=255, choices=SCRAPER_REDEEM_TOKEN_TYPE, default='envato', null=False,
                                  blank=False,
                                  verbose_name='نوع توکن')
    token_unique_code = models.CharField(max_length=255, null=False, blank=False, editable=False,
                                         verbose_name='کد یکتا')
    total_tokens = models.PositiveIntegerField(null=False, blank=False, verbose_name='تعداد کل')
    daily_allowed_number = models.PositiveIntegerField(null=False, blank=False, verbose_name='تعداد مجاز روزانه')
    expiry_days = models.PositiveSmallIntegerField(default=90, null=False, blank=False,
                                                   verbose_name="تعداد روز انقضا پس از ردیم شدن")
    created_at = jmodel.jDateTimeField(auto_now_add=True, verbose_name="تاریخ و زمان ایجاد")

    is_used = models.BooleanField(default=False, verbose_name='استفاده شده')

    def __str__(self):
        return f'token_name: {self.token_name} | token_type: {self.token_type} | token_unique_code: {self.token_unique_code}'

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'ردیم توکن خزنده'
        verbose_name_plural = 'ردیم توکن های خزندگان'

    def save(self, *args, **kwargs):
        if not self.token_unique_code:
            self.token_unique_code = token_generator(self.token_type)
        super().save(*args, **kwargs)


def token_generator(token_type):
    letters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    redeem_code = ''
    for i in range(1, 17):
        redeem_code += letters[random.randint(0, 25)]
        if i % 4 == 0 and i != 16:
            redeem_code += '-'
    if token_type == 'motion_array':
        redeem_code = f'Motion-{redeem_code}'
    elif token_type == 'envato':
        redeem_code = f'Envato-{redeem_code}'
    else:
        redeem_code = f'{redeem_code}'
    return redeem_code


class UserWalletChargeHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=False, blank=False, editable=False,
                             verbose_name='کاربر')
    redeemed_token = models.OneToOneField(WalletRedeemToken, related_name='user_wallet_charge_history_redeemed_token',
                                          on_delete=models.CASCADE, blank=False, editable=False,
                                          verbose_name='توکن ردیم شده')
    created_at = jmodel.jDateTimeField(auto_now_add=True, verbose_name="تاریخ و زمان")

    def __str__(self):
        return self.user.username + " | " + str(self.redeemed_token.token_unique_code)

    class Meta:
        ordering = ['user', '-created_at', ]
        verbose_name = 'تاریخچه شارژ حساب'
        verbose_name_plural = 'تاریخچه شارژ های حساب'


class UserScraperTokenRedeemHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=False, blank=False, editable=False,
                             verbose_name='کاربر')
    redeemed_token = models.OneToOneField(ScraperRedeemToken,
                                          related_name='user_scraper_token_redeem_history_redeemed_token',
                                          on_delete=models.CASCADE, blank=False, editable=False,
                                          verbose_name='توکن ردیم شده')
    created_at = jmodel.jDateTimeField(auto_now_add=True, verbose_name="تاریخ و زمان")

    def __str__(self):
        return self.user.username + " | " + str(self.redeemed_token.token_unique_code)

    class Meta:
        ordering = ['user', '-created_at', ]
        verbose_name = 'تاریخچه ردیم توکن خزنده'
        verbose_name_plural = 'تاریخچه ردیم توکن های خزندگان'


class UserFileHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=False, blank=False, editable=False,
                             verbose_name='کاربر')
    media = models.ForeignKey(File, on_delete=models.CASCADE, null=False, blank=False, editable=False,
                              verbose_name='فایل دریافت شده')
    created_at = jmodel.jDateTimeField(auto_now_add=True, verbose_name="تاریخ و زمان درخواست")

    def __str__(self):
        return self.user.username + " | " + str(self.media.file.name)

    class Meta:
        ordering = ['-created_at', ]
        verbose_name = 'تاریخچه فایل دریافتی کاربر'
        verbose_name_plural = 'تاریخچه فایل های دریافتی کاربر'


class UserRequestHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=False, blank=False, editable=False,
                             verbose_name='کاربر')
    files = models.ManyToManyField(File, blank=False, editable=False, verbose_name='فایل های متصل به این درخواست')
    # files_links = models.ManyToManyField(UserFileLink, blank=False, verbose_name='لینک موقت فایل های متصل به این درخواست')
    has_finished = models.BooleanField(default=False, editable=False, verbose_name='تکمیل شده')
    data_track = models.CharField(max_length=1000, null=False, blank=False, editable=False, verbose_name='داده ها')
    created_at = jmodel.jDateTimeField(auto_now_add=True, verbose_name="تاریخ و زمان درخواست")

    def __str__(self):
        return self.user.username + " | " + str(self.created_at.date())

    class Meta:
        ordering = ['-created_at', ]
        verbose_name = 'تاریخچه درخواست'
        verbose_name_plural = 'تاریخچه درخواست ها'


class UserRequestHistoryDetail(models.Model):
    user_request_history = models.OneToOneField(UserRequestHistory, related_name='user_request_history_detail',
                                                on_delete=models.CASCADE, null=False, blank=False, editable=False,
                                                verbose_name='تاریخچه درخواست کاربر')
    telegram_chat_id = models.CharField(max_length=255, null=False, blank=False, editable=False,
                                        verbose_name='ایدی چت تلگرام')
    telegram_message_id = models.CharField(max_length=255, null=False, blank=False, editable=False,
                                           verbose_name='ایدی پیام تلگرام')
    created_at = jmodel.jDateTimeField(auto_now_add=True, verbose_name="تاریخ و زمان درخواست")

    def __str__(self):
        return f'user: {self.user_request_history.user.username}'

    class Meta:
        ordering = ['-created_at', ]
        verbose_name = 'تاریخچه درخواست - جزئیات'
        verbose_name_plural = 'تاریخچه درخواست ها - جزئیات'
