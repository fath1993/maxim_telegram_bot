from django.contrib import admin

from motionarray.models import MotionArraySetting, MotionArrayAccount


@admin.register(MotionArraySetting)
class MotionArraySettingAdmin(admin.ModelAdmin):
    list_display = (
        'sleep_time',
        'motion_array_thread_number',
        'motion_array_queue_number',
    )

    fields = (
        'sleep_time',
        'motion_array_thread_number',
        'motion_array_queue_number',
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
    )

    fields = (
        'motion_array_user',
        'motion_array_pass',
        'motion_array_cookie',
        'motion_array_account_description',
        'limited_date',
        'is_account_active',
    )



