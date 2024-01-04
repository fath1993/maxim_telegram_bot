from django.contrib import admin

from core.models import CoreSetting, TelegramBotSetting, File, CustomMessage


@admin.register(CoreSetting)
class CoreSettingAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'daily_download_limit',
        'envato_scraper_is_active',
        'under_construction',
    )

    fields = (
        'daily_download_limit',
        'envato_scraper_is_active',
        'under_construction',
    )

    def has_add_permission(self, request):
        if CoreSetting.objects.filter().count() == 0:
            return True
        else:
            return False


@admin.register(TelegramBotSetting)
class TelegramBotSettingAdmin(admin.ModelAdmin):
    list_display = (
        'bot_address',
        'bot_token',
    )

    fields = (
        'bot_address',
        'bot_token',
    )


@admin.action(description="خروج از وضعیت در حال دانلود")
def make_in_progress_false(self, request, queryset):
    queryset.update(in_progress=False)


@admin.register(File)
class FileAdmin(admin.ModelAdmin):
    list_display = (
        'file_type',
        'page_link',
        'unique_code',
        'file_storage_link',
        'download_percentage',
        'failed_repeat',
        'is_acceptable_file',
        'in_progress',
        'created_at_display',
        'updated_at_display',
    )

    list_filter = (
        'is_acceptable_file',
        'in_progress',
    )

    search_fields = (
        'unique_code',
    )

    readonly_fields = (
        'created_at',
        'updated_at',
    )

    fields = (
        'file_type',
        'page_link',
        'unique_code',
        'file_storage_link',
        'file',
        'download_percentage',
        'failed_repeat',
        'in_progress',
        'is_acceptable_file',
        'created_at',
        'updated_at',
    )

    @admin.display(description='تاریخ ایجاد', empty_value='???')
    def created_at_display(self, obj):
        return obj.created_at.strftime('%Y-%m-%d %H:%M')

    @admin.display(description='تاریخ بروزرسانی', empty_value='???')
    def updated_at_display(self, obj):
        return obj.updated_at.strftime('%Y-%m-%d %H:%M')

    actions = [make_in_progress_false]


@admin.register(CustomMessage)
class CustomMessageAdmin(admin.ModelAdmin):
    list_display = (
        'key',
        'message',
    )

    fields = (
        'key',
        'message',
    )
