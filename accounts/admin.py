from django.contrib import admin
from accounts.models import Profile, UserRequestHistory, RedeemDownloadToken, UserRedeemHistory, UserFileHistory, \
    UserRequestHistoryDetail, SingleToken, MultiToken


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'user_telegram_phone_number',
        'daily_limit',
        'daily_used_total',
        'multi_token_daily_used',
        'updated_at_display',
    )

    readonly_fields = (
        'user_latest_requested_files',
        'updated_at',
    )

    fields = (
        'user',
        'user_telegram_phone_number',
        'profile_pic',
        'daily_limit',
        'daily_used_total',
        'multi_token_daily_used',
        'single_tokens',
        'multi_token',
        'user_latest_requested_files',
        'updated_at',
    )

    @admin.display(description='تاریخ بروزرسانی', empty_value='???')
    def updated_at_display(self, obj):
        return obj.updated_at.strftime('%Y-%m-%d %H:%M')


@admin.register(RedeemDownloadToken)
class RedeemDownloadTokenAdmin(admin.ModelAdmin):
    list_display = (
        'token_name',
        'token_type',
        'token_unique_code',
        'tokens_count',
        'is_used',
        'expiry_days',
        'created_at_display',
    )

    readonly_fields = (
        'token_unique_code',
        'created_at',
    )

    fields = (
        'token_name',
        'token_type',
        'tokens_count',
        'is_used',
        'expiry_days',
        'created_at',
        'token_unique_code',
    )

    @admin.display(description='تاریخ ایجاد', empty_value='???')
    def created_at_display(self, obj):
        return obj.created_at.strftime('%Y-%m-%d %H:%M')


@admin.register(UserRedeemHistory)
class UserRedeemHistoryAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'redeemed_token',
        'created_at',
    )

    readonly_fields = (
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


@admin.register(UserRequestHistory)
class UserRequestHistoryAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'has_finished',
        'created_at',
    )

    list_filter = (
        'has_finished',
    )

    readonly_fields = (
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


admin.site.register(UserFileHistory)
admin.site.register(UserRequestHistoryDetail)



@admin.register(SingleToken)
class SingleTokenAdmin(admin.ModelAdmin):
    list_display = (
        'is_used',
        'expiry_date',
    )

    readonly_fields = (
        'is_used',
        'expiry_date',
    )

    fields = (
        'is_used',
        'expiry_date',
    )

    def has_add_permission(self, request):
        return False


@admin.register(MultiToken)
class MultiTokenAdmin(admin.ModelAdmin):
    list_display = (
        'is_used',
        'daily_count',
        'expiry_date',
    )

    readonly_fields = (
        'is_used',
        'daily_count',
        'expiry_date',
    )

    fields = (
        'is_used',
        'daily_count',
        'expiry_date',
    )

    def has_add_permission(self, request):
        return False