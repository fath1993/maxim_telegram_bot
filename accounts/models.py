import random
import uuid

import jdatetime
from django.contrib.auth.models import User
from django.urls import reverse
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django_jalali.db import models as jmodel

from core.models import File, get_core_settings, CustomMessage

TOKEN_TYPE = (('single', 'single'), ('multiple', 'multiple'))


class SingleToken(models.Model):
    is_used = models.BooleanField(default=False, editable=False, verbose_name='استفاده شده')
    expiry_date = jmodel.jDateTimeField(null=False, blank=False, editable=False, verbose_name="تاریخ و زمان انقضا")

    def __str__(self):
        return f'is_used: {self.is_used} | expiry_date: {self.expiry_date.strftime("%Y/%m/%d")}'

    class Meta:
        verbose_name = 'توکن تکی'
        verbose_name_plural = 'توکن های تکی'


class MultiToken(models.Model):
    is_used = models.BooleanField(default=False, editable=False, verbose_name='استفاده شده')
    daily_count = models.PositiveSmallIntegerField(null=False, blank=False, editable=False, verbose_name='تعداد روزانه')
    expiry_date = jmodel.jDateTimeField(null=False, blank=False, editable=False, verbose_name="تاریخ و زمان انقضا")

    def __str__(self):
        return f'is_used: {self.is_used} | daily_count: {self.daily_count} | expiry_date: {self.expiry_date.strftime("%Y/%m/%d")}'

    class Meta:
        verbose_name = 'توکن چند تایی'
        verbose_name_plural = 'توکن های چند تایی'


class Profile(models.Model):
    user = models.OneToOneField(User, related_name='user_profile', on_delete=models.CASCADE, null=False, blank=False, verbose_name='کاربر')
    user_telegram_phone_number = models.CharField(max_length=255, null=True, blank=True,
                                                  verbose_name='شماره تماس اکانت تلگرام')
    profile_pic = models.ImageField(null=True, blank=True, verbose_name='عکس پروفایل')
    daily_limit = models.PositiveIntegerField(default=0, null=False, blank=False,
                                                          verbose_name='تعداد درخواست های مجاز روزانه')
    daily_used_total = models.PositiveIntegerField(default=0, null=False, blank=False,
                                              verbose_name='تعداد کل موارد درخواست شده طی آخرین روز')
    multi_token_daily_used = models.PositiveIntegerField(default=0, null=False, blank=False,
                                             verbose_name='تعداد موارد درخواست شده طی آخرین روز توسط توکن روزانه')
    single_tokens = models.ManyToManyField(SingleToken, blank=True, verbose_name='توکن های تکی')
    multi_token = models.ForeignKey(MultiToken, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='توکن چند تایی')
    user_latest_requested_files = models.TextField(null=True, blank=True, editable=False, verbose_name='آخرین فایل های درخواستی کاربر')
    updated_at = jmodel.jDateTimeField(auto_now=True, verbose_name="تاریخ و زمان بروز رسانی")

    def __str__(self):
        return self.user.username

    class Meta:
        ordering = ['-user__id', ]
        verbose_name = 'پروفایل'
        verbose_name_plural = 'پروفایل'

    def get_absolute_url(self):
        return reverse('accounts:profile-with-user-id', kwargs={'user_id': self.id})

    def save(self, *args, **kwargs):
        try:
            if self.updated_at.day != jdatetime.datetime.now().day:
                self.multi_token_daily_used = 0
                self.daily_used_total = 0
            super().save(*args, **kwargs)
        except:
            super().save(*args, **kwargs)


@receiver(post_save, sender=User)
def auto_create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance, daily_limit=get_core_settings().daily_download_limit)
        if instance.username == 'admin':
            pre_defined_messages = {
                'telegram_message_start': '',
                'telegram_message_download_help': '',
                'telegram_message_download_file': '',
                'telegram_message_download_from_envato_elements': '',
                'telegram_message_login': '',
                'telegram_message_change_language': '',
                'telegram_message_partnership': '',
                'telegram_message_wallet_charge': '',
                'telegram_message_support': '',
                'telegram_message_support_callback_yes': '',
                'telegram_message_about': '',
                'telegram_message_help': '',
                'telegram_message_profile_menu': '',
                'redeem_new_token': '',
                'under_construction_check': '',
                'message_is_acceptable_check': '',
                'user_quote_limit_check': '',
                'user_has_active_plan_check': '',
                'telegram_message_check': '',
            }
            for key in pre_defined_messages:
                try:
                    custom_message = CustomMessage.objects.get(key=key)
                except:
                    custom_message = CustomMessage.objects.create(
                        key=key,
                        message=pre_defined_messages[key]
                    )


class RedeemDownloadToken(models.Model):
    token_name = models.CharField(max_length=255, null=True, blank=True, verbose_name='نام توکن')
    token_type = models.CharField(max_length=255, choices=TOKEN_TYPE, default='single', null=False, blank=False,
                                  verbose_name='نوع توکن')
    token_unique_code = models.CharField(max_length=255, null=False, blank=False, editable=False, verbose_name='کد یکتا')
    tokens_count = models.PositiveSmallIntegerField(default=1, null=False, blank=False, verbose_name='تعداد')
    is_used = models.BooleanField(default=False, verbose_name='استفاده شده')
    expiry_days = models.PositiveSmallIntegerField(default=90, null=False, blank=False, verbose_name="تعداد روز انقضا پس از ردیم شدن")
    created_at = jmodel.jDateTimeField(auto_now_add=True, verbose_name="تاریخ و زمان ایجاد")

    def __str__(self):
        return self.token_type + " | " + self.token_unique_code

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'ردیم توکن دانلود'
        verbose_name_plural = 'ردیم توکن های دانلود'

    def save(self, *args, **kwargs):
        if not self.token_unique_code:
            self.token_unique_code = token_generator()
        super().save(*args, **kwargs)


def token_generator():
    letters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    redeem_code = ''
    for i in range(1, 17):
        redeem_code += letters[random.randint(0, 25)]
        if i % 4 == 0 and i != 16:
            redeem_code += '-'
    print(redeem_code)
    return redeem_code


class UserRedeemHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=False, blank=False, verbose_name='کاربر')
    redeemed_token = models.OneToOneField(RedeemDownloadToken, related_name='user_redeem_history_redeemed_token', on_delete=models.CASCADE, blank=False,
                                          verbose_name='توکن ردیم شده')
    created_at = jmodel.jDateTimeField(auto_now_add=True, verbose_name="تاریخ و زمان")

    def __str__(self):
        return self.user.username + " | " + str(self.redeemed_token.token_unique_code)

    class Meta:
        ordering = ['user', '-created_at', ]
        verbose_name = 'تاریخچه ردیم'
        verbose_name_plural = 'تاریخچه ردیم ها'


class UserFileHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=False, blank=False, verbose_name='کاربر')
    media = models.ForeignKey(File, on_delete=models.CASCADE, null=False, blank=False, verbose_name='فایل دریافت شده')
    created_at = jmodel.jDateTimeField(auto_now_add=True, verbose_name="تاریخ و زمان درخواست")

    def __str__(self):
        return self.user.username + " | " + str(self.media.file.name)

    class Meta:
        ordering = ['-created_at', ]
        verbose_name = 'تاریخچه فایل دریافتی کاربر'
        verbose_name_plural = 'تاریخچه فایل های دریافتی کاربر'


# class UserFileLink(models.Model):
#     user = models.ForeignKey(User, on_delete=models.CASCADE, null=False, blank=False, verbose_name='کاربر')
#     files = models.ManyToManyField(File, blank=False, verbose_name='فایل های متصل به این درخواست')
#     short_sign_of_link = models.CharField(max_length=255, null=False, blank=False, verbose_name='علامت اختصاری لینک')
#     links = models.CharField(max_length=255, null=False, blank=False, verbose_name='لینک')
#     created_at = jmodel.jDateTimeField(auto_now_add=True, verbose_name="تاریخ و زمان ایجاد")
#
#     def __str__(self):
#         return f'short_sign_of_link: {self.short_sign_of_link}'
#
#     class Meta:
#         verbose_name = 'لینک مختصر'
#         verbose_name_plural = 'لینک مختصر'


class UserRequestHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=False, blank=False, verbose_name='کاربر')
    files = models.ManyToManyField(File, blank=False, verbose_name='فایل های متصل به این درخواست')
    # files_links = models.ManyToManyField(UserFileLink, blank=False, verbose_name='لینک موقت فایل های متصل به این درخواست')
    has_finished = models.BooleanField(default=False, verbose_name='تکمیل شده')
    data_track = models.CharField(max_length=1000, null=False, blank=False, editable=False, verbose_name='داده ها')
    created_at = jmodel.jDateTimeField(auto_now_add=True, verbose_name="تاریخ و زمان درخواست")

    def __str__(self):
        return self.user.username + " | " + str(self.created_at.date())

    class Meta:
        ordering = ['-created_at', ]
        verbose_name = 'تاریخچه درخواست'
        verbose_name_plural = 'تاریخچه درخواست ها'


class UserRequestHistoryDetail(models.Model):
    user_request_history = models.OneToOneField(UserRequestHistory, related_name='user_request_history_detail', on_delete=models.CASCADE, null=False, blank=False, verbose_name='تاریخچه درخواست کاربر')
    telegram_chat_id = models.CharField(max_length=255, null=False, blank=False, editable=False,
                                        verbose_name='ایدی چت تلگرام')
    telegram_message_id = models.CharField(max_length=255, null=False, blank=False, editable=False,
                                           verbose_name='ایدی پیام تلگرام')
    created_at = jmodel.jDateTimeField(auto_now_add=True, verbose_name="تاریخ و زمان درخواست")

    def __str__(self):
        return f'user: {self.user_request_history.user.username}'

    class Meta:
        verbose_name = 'جزئیات تاریخچه درخواست'
        verbose_name_plural = 'جزئیات تاریخچه درخواست ها'