from django.contrib.auth.models import User
from django.db import models
from django_jalali.db import models as jmodel


class Message(models.Model):
    title = models.CharField(max_length=255, null=True, blank=True, verbose_name='عنوان')
    description = models.TextField(null=True, blank=True, verbose_name='توضیحات')
    file = models.FileField(upload_to='message-files/', null=True, blank=True, verbose_name='فایل ضمیمه')
    receivers = models.ManyToManyField(User, blank=True, verbose_name='دریافت کنندگان')
    created_at = jmodel.jDateTimeField(auto_now_add=True, verbose_name='تاریخ و زمان ایجاد')

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-created_at', ]
        verbose_name = 'پیام'
        verbose_name_plural = 'پیام ها'


    def save(self, *args, **kwargs):
        if not self.title and not self.description:
            pass
        else:
            super().save(*args, **kwargs)