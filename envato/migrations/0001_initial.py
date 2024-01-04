# Generated by Django 4.2.7 on 2024-01-04 15:26

from django.db import migrations, models
import django_jalali.db.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='EnvatoAccount',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('envato_user', models.CharField(blank=True, max_length=255, null=True, verbose_name='نام کاربری انواتو')),
                ('envato_pass', models.CharField(blank=True, max_length=255, null=True, verbose_name='کلمه عبور انواتو')),
                ('envato_cookie', models.FileField(blank=True, null=True, upload_to='envato/cookies', verbose_name='کوکی انواتو')),
                ('envato_account_description', models.CharField(blank=True, max_length=255, null=True, verbose_name='توضیحات')),
                ('limited_date', django_jalali.db.models.jDateTimeField(blank=True, null=True, verbose_name='تاریخ و زمان لیمیت')),
                ('is_account_active', models.BooleanField(default=True, verbose_name='آیا اکانت فعال است؟')),
            ],
            options={
                'verbose_name': 'اکانت انواتو',
                'verbose_name_plural': 'اکانت های انواتو',
                'ordering': ['id'],
            },
        ),
        migrations.CreateModel(
            name='EnvatoSetting',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sleep_time', models.PositiveSmallIntegerField(default=5, verbose_name='زمان توقف ربات بین هر کوئری')),
                ('envato_thread_number', models.PositiveSmallIntegerField(default=4, verbose_name='تعداد پردازش همزمان انواتو')),
                ('envato_queue_number', models.PositiveSmallIntegerField(default=4, verbose_name='تعداد پردازش صف انواتو')),
            ],
            options={
                'verbose_name': 'تنظیمات انواتو',
                'verbose_name_plural': 'تنظیمات انواتو',
            },
        ),
    ]
