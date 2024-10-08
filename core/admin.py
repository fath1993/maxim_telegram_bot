import io

import jdatetime
from django.contrib import admin
from django.http import HttpResponse
from openpyxl.workbook import Workbook

from core.models import CoreSetting, TelegramBotSetting, File, AriaCode, FileQualityCostFactor, \
    FileFormatCostFactor


@admin.register(AriaCode)
class AriaCodeAdmin(admin.ModelAdmin):
    list_display = (
        'aria_code',
    )

    search_fields = (
        'aria_code',
    )

    fields = (
        'aria_code',
    )


@admin.register(FileFormatCostFactor)
class FileFormatCostFactorAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'cost_factor',
    )

    fields = (
        'name',
        'cost_factor',
    )


@admin.register(FileQualityCostFactor)
class FileQualityCostFactorAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'cost_factor',
    )

    fields = (
        'name',
        'cost_factor',
    )


@admin.register(CoreSetting)
class CoreSettingAdmin(admin.ModelAdmin):
    list_display = (
        '__str__',
    )

    fields = (
        'thread_number',
        'queue_number',
        'envato_scraper_is_active',
        'envato_account_total_daily_limit',
        'envato_account_daily_bandwidth_limit',
        'envato_cost_factor',

        'motion_array_scraper_is_active',
        'motion_array_account_total_daily_limit',
        'motion_array_account_daily_bandwidth_limit',
        'motion_array_cost_factor',

        'service_under_construction',
        'error_description',
        'aria_code_acceptance',
        'file_format_cost_factors',
        'file_quality_cost_factors',
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
        'file_meta',
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
        'file_meta',
        'created_at',
        'updated_at',
    )

    @admin.display(description='تاریخ ایجاد', empty_value='???')
    def created_at_display(self, obj):
        return obj.created_at.strftime('%Y-%m-%d %H:%M')

    @admin.display(description='تاریخ بروزرسانی', empty_value='???')
    def updated_at_display(self, obj):
        return obj.updated_at.strftime('%Y-%m-%d %H:%M')

    actions = (
        'export_files_as_csv',
        'make_in_progress_false',
    )

    @admin.action(description='خروجی اکسل')
    def export_files_as_csv(self, request, queryset):
        return export_files_as_csv(queryset)


def export_files_as_csv(queryset):
    output = io.BytesIO()
    wb = Workbook()
    ws = wb.active

    ws.append(['file_type', 'page_link', 'unique_code', 'file_storage_link', 'file', 'download_percentage',
               'is_acceptable_file', 'in_progress', 'failed_repeat', 'file_meta', ])
    for obj in queryset:
        ws.append([f'{obj.file_type}', f'{obj.page_link}', f'{obj.unique_code}', f'{obj.file_storage_link}',
                   f'{obj.file}', f'{obj.download_percentage}',
                   f'{obj.is_acceptable_file}', f'{obj.in_progress}', f'{obj.failed_repeat}',
                   f'{obj.file_meta}', ])

    now = jdatetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S')

    # Save the workbook to the in-memory byte stream
    wb.save(output)
    output.seek(0)
    response = HttpResponse(
        output.read(),
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = f'attachment; filename={now}-files.xlsx'

    return response
