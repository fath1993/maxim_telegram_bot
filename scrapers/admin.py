from django.contrib import admin

from scrapers.models import EnvatoSetting, EnvatoAccount, MotionArraySetting, MotionArrayAccount


@admin.register(EnvatoSetting)
class EnvatoSettingAdmin(admin.ModelAdmin):
    list_display = (
        'sleep_time',
    )

    fields = (
        'sleep_time',
    )


@admin.register(EnvatoAccount)
class EnvatoAccountAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'envato_user',
        'envato_pass',
        'envato_cookie',
        'envato_account_description',
        'limited_date',
        'is_account_active',

        'number_of_daily_usage',
        # 'daily_bandwidth_usage',
    )

    readonly_fields = (
        'number_of_daily_usage',
        'daily_bandwidth_usage',
    )

    fields = (
        'envato_user',
        'envato_pass',
        'envato_cookie',
        'envato_account_description',
        'limited_date',
        'is_account_active',

        'number_of_daily_usage',
        # 'daily_bandwidth_usage',
    )


@admin.register(MotionArraySetting)
class MotionArraySettingAdmin(admin.ModelAdmin):
    list_display = (
        'sleep_time',
        'download_highest_available_quality',
    )

    fields = (
        'sleep_time',
        'download_highest_available_quality',
    )


@admin.register(MotionArrayAccount)
class MotionArrayAccountAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'motion_array_user',
        'motion_array_pass',
        'motion_array_cookie',
        'motion_array_account_description',
        'limited_date',
        'is_account_active',

        'number_of_daily_usage',
        # 'daily_bandwidth_usage',
    )

    readonly_fields = (
        'number_of_daily_usage',
        # 'daily_bandwidth_usage',
    )

    fields = (
        'motion_array_user',
        'motion_array_pass',
        'motion_array_cookie',
        'motion_array_account_description',
        'limited_date',
        'is_account_active',

        'number_of_daily_usage',
        # 'daily_bandwidth_usage',
    )
