import jdatetime
from django import template
from django.contrib.auth.models import User

from accounts.models import UserFileHistory
from core.views import user_financial_state
from custom_logs.models import custom_log

register = template.Library()


@register.filter
def all_user():
    users = User.objects.filter().order_by('id')
    return users


@register.filter
def get_user_all_download_number(user):
    user_file_history = UserFileHistory.objects.filter(user=user)
    return user_file_history.count()


@register.filter
def get_user_latest_download_number(user):
    user_file_history = UserFileHistory.objects.filter(user=user)
    i = 0
    for user_file in user_file_history:
        if user_file.created_at.strftime("%Y-%m-%d") == jdatetime.datetime.now().strftime("%Y-%m-%d"):
            i += 1
    return i


@register.filter
def get_user_financial_state(user, arg):
    user_financial_state_result = user_financial_state(user)
    w_cr = user_financial_state_result['wallet_credit']

    en_has_active_token = user_financial_state_result['user_envato_state']['has_active_token']
    en_total_remaining_tokens = user_financial_state_result['user_envato_state']['total_remaining_tokens']
    en_daily_remaining_tokens = user_financial_state_result['user_envato_state']['daily_remaining_tokens']
    en_total_tokens = user_financial_state_result['user_envato_state']['total_tokens']
    en_daily_allowed_number = user_financial_state_result['user_envato_state']['daily_allowed_number']
    en_expiry_date = user_financial_state_result['user_envato_state']['expiry_date']

    ma_has_active_token = user_financial_state_result['user_motion_array_state']['has_active_token']
    ma_total_remaining_tokens = user_financial_state_result['user_motion_array_state']['total_remaining_tokens']
    ma_daily_remaining_tokens = user_financial_state_result['user_motion_array_state']['daily_remaining_tokens']
    ma_total_tokens = user_financial_state_result['user_motion_array_state']['total_tokens']
    ma_daily_allowed_number = user_financial_state_result['user_motion_array_state']['daily_allowed_number']
    ma_expiry_date = user_financial_state_result['user_motion_array_state']['expiry_date']

    message = f''''''

    if arg == 'wallet_credit':
        return w_cr
    elif arg == 'has_envato_token':
        if en_has_active_token:
            return 'دارد'
        else:
            return 'ندارد'
    elif arg == 'has_motion_token':
        if ma_has_active_token:
            return 'دارد'
        else:
            return 'ندارد'
    elif arg == 'envato_token_detail':
        message += f'تاریخ انقضا بسته: {en_expiry_date}'
        message += f'\n'
        message += f'تعداد مصرف شده در 24 ساعت: {en_daily_allowed_number - en_daily_remaining_tokens} از {en_daily_allowed_number}'
        message += f'\n'
        message += f'تعداد مصرف شده کل: {en_total_tokens - en_total_remaining_tokens} از {en_total_tokens}'
        message += f'\n'
        return message
    elif arg == 'motion_token_detail':
        message += f'تاریخ انقضا بسته: {ma_expiry_date}'
        message += f'\n'
        message += f'تعداد مصرف شده در 24 ساعت: {ma_daily_allowed_number - ma_daily_remaining_tokens} از {ma_daily_allowed_number}'
        message += f'\n'
        message += f'تعداد مصرف شده کل: {ma_total_tokens - ma_total_remaining_tokens} از {ma_total_tokens}'
        message += f'\n'
        return message
    else:
        return 'None'
