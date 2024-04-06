import io

import jdatetime
from django.contrib import admin
from django.http import HttpResponse
from openpyxl import Workbook

from accounts.models import Profile, UserRequestHistory, UserFileHistory, \
    UserRequestHistoryDetail, UserMultiToken, WalletRedeemToken, ScraperRedeemToken, UserWalletChargeHistory, \
    UserScraperTokenRedeemHistory


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'user_telegram_phone_number',
        'wallet_credit',
        'updated_at_display',
    )

    readonly_fields = (
        'user',
        'user_latest_requested_files',
        'updated_at',
    )

    fields = (
        'user',
        'user_telegram_phone_number',
        'wallet_credit',
        'user_latest_requested_files',
        'updated_at',
    )

    @admin.display(description='تاریخ بروزرسانی', empty_value='???')
    def updated_at_display(self, obj):
        return obj.updated_at.strftime('%Y-%m-%d %H:%M')


@admin.register(UserMultiToken)
class UserMultiTokenAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'user',
        'token_type',
        'disabled',
    )

    list_filter = (
        'disabled',
    )

    readonly_fields = (
        'user',
        'token_type',
        'latest_usage_date',
        'total_remaining_tokens',
        'daily_remaining_tokens',

        'token_unique_code',
        'total_tokens',
        'daily_allowed_number',
        'expiry_date',
        'expiry_days',

        'disabled',
    )

    fields = (
        'user',
        'token_type',
        'latest_usage_date',
        'total_remaining_tokens',
        'daily_remaining_tokens',

        'token_unique_code',
        'total_tokens',
        'daily_allowed_number',
        'expiry_date',
        'expiry_days',

        'disabled',
    )

    def has_add_permission(self, request):
        return False


@admin.register(WalletRedeemToken)
class WalletRedeemTokenAdmin(admin.ModelAdmin):
    list_display = (
        'token_unique_code',
        'charge_amount',
        'created_at_display',

        'is_used',
    )

    list_filter = (
        'is_used',
    )

    readonly_fields = (
        'token_unique_code',
        'is_used',
        'created_at',
    )

    fields = (
        'token_unique_code',
        'charge_amount',
        'created_at',

        'is_used',
    )

    actions = (
        'export_token_as_csv',
    )

    @admin.display(description='تاریخ ایجاد', empty_value='???')
    def created_at_display(self, obj):
        return obj.created_at.strftime('%Y-%m-%d %H:%M')

    @admin.action(description='خروجی اکسل')
    def export_token_as_csv(self, request, queryset):
        return export_tokens_as_csv(queryset)


@admin.register(ScraperRedeemToken)
class ScraperRedeemTokenAdmin(admin.ModelAdmin):
    list_display = (
        'token_name',
        'token_type',
        'token_unique_code',
        'total_tokens',
        'daily_allowed_number',
        'expiry_days',
        'created_at_display',

        'is_used',
    )

    list_filter = (
        'is_used',
        'token_type',
    )

    readonly_fields = (
        'token_unique_code',
        'is_used',
        'created_at',
    )

    fields = (
        'token_name',
        'token_type',
        'token_unique_code',
        'total_tokens',
        'daily_allowed_number',
        'expiry_days',
        'created_at',

        'is_used',
    )

    actions = (
        'export_token_as_csv',
    )

    @admin.display(description='تاریخ ایجاد', empty_value='???')
    def created_at_display(self, obj):
        return obj.created_at.strftime('%Y-%m-%d %H:%M')

    @admin.action(description='خروجی اکسل')
    def export_token_as_csv(self, request, queryset):
        return export_tokens_as_csv(queryset)


@admin.register(UserWalletChargeHistory)
class UserWalletChargeHistoryAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'redeemed_token',
        'created_at_display',
    )

    readonly_fields = (
        'user',
        'redeemed_token',
        'created_at',
    )

    fields = (
        'user',
        'redeemed_token',
        'created_at',
    )

    @admin.display(description='تاریخ ایجاد', empty_value='???')
    def created_at_display(self, obj):
        return obj.created_at.strftime('%Y-%m-%d %H:%M')

    def has_add_permission(self, request):
        return False


@admin.register(UserScraperTokenRedeemHistory)
class UserScraperTokenRedeemHistoryAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'redeemed_token',
        'created_at_display',
    )

    readonly_fields = (
        'user',
        'redeemed_token',
        'created_at',
    )

    fields = (
        'user',
        'redeemed_token',
        'created_at',
    )

    @admin.display(description='تاریخ ایجاد', empty_value='???')
    def created_at_display(self, obj):
        return obj.created_at.strftime('%Y-%m-%d %H:%M')

    def has_add_permission(self, request):
        return False


@admin.register(UserRequestHistory)
class UserRequestHistoryAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'has_finished',
        'created_at_display',
    )

    list_filter = (
        'has_finished',
    )

    readonly_fields = (
        'user',
        'files',
        'has_finished',
        'data_track',
        'created_at',
    )

    fields = (
        'user',
        'files',
        'has_finished',
        'data_track',
        'created_at',
    )

    @admin.display(description='تاریخ بروزرسانی', empty_value='???')
    def created_at_display(self, obj):
        return obj.created_at.strftime('%Y-%m-%d %H:%M')

    def has_add_permission(self, request):
        return False


@admin.register(UserFileHistory)
class UserFileHistoryAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'media',
        'created_at_display',
    )

    readonly_fields = (
        'user',
        'media',
        'created_at',
    )

    fields = (
        'user',
        'media',
        'created_at',
    )

    @admin.display(description='تاریخ بروزرسانی', empty_value='???')
    def created_at_display(self, obj):
        return obj.created_at.strftime('%Y-%m-%d %H:%M')

    def has_add_permission(self, request):
        return False


@admin.register(UserRequestHistoryDetail)
class UserRequestHistoryDetailAdmin(admin.ModelAdmin):
    list_display = (
        'user_request_history',
        'telegram_chat_id',
        'telegram_message_id',
        'created_at_display',
    )

    readonly_fields = (
        'user_request_history',
        'telegram_chat_id',
        'telegram_message_id',
        'created_at',
    )

    fields = (
        'user_request_history',
        'telegram_chat_id',
        'telegram_message_id',
        'created_at',
    )

    @admin.display(description='تاریخ بروزرسانی', empty_value='???')
    def created_at_display(self, obj):
        return obj.created_at.strftime('%Y-%m-%d %H:%M')

    def has_add_permission(self, request):
        return False


def export_tokens_as_csv(queryset):
    output = io.BytesIO()
    wb = Workbook()
    ws = wb.active

    ws.append(['ضمائم', ])
    for obj in queryset:
        ws.append([f'{obj.token_unique_code}, '])

    now = jdatetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S')

    # Save the workbook to the in-memory byte stream
    wb.save(output)
    output.seek(0)
    response = HttpResponse(
        output.read(),
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = f'attachment; filename={now}-tokens.xlsx'

    return response