from django.contrib import admin

from envato.models import EnvatoSetting, EnvatoAccount


@admin.register(EnvatoSetting)
class EnvatoSettingAdmin(admin.ModelAdmin):
    list_display = (
        'sleep_time',
        'envato_thread_number',
        'envato_queue_number',
    )

    fields = (
        'sleep_time',
        'envato_thread_number',
        'envato_queue_number',
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
    )

    fields = (
        'envato_user',
        'envato_pass',
        'envato_cookie',
        'envato_account_description',
        'limited_date',
        'is_account_active',
    )



