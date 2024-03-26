from django.contrib.auth.models import User
from django.http import JsonResponse
from django.test import TestCase

from core.views import telegram_response_check, under_construction_check, \
    check_user_phone_number_is_allowed_to_register, telegram_message_start_first_time, \
    telegram_message_phone_number_is_not_allowed, telegram_message_confirm_phone_number_warning, telegram_message_start, \
    telegram_message_download_help, telegram_message_download_file, telegram_message_download_from_envato_elements, \
    telegram_message_login, telegram_message_change_language, telegram_message_partnership, \
    telegram_message_download_list, telegram_message_financial_report, telegram_message_wallet_charge, \
    telegram_wallet_charge_callback_main_page, telegram_message_account_state, telegram_message_support, \
    telegram_message_support_callback_yes, telegram_message_support_callback_no, telegram_message_about, \
    telegram_message_help, telegram_message_profile_menu, telegram_message_fetch_data_accept_1, \
    telegram_message_fetch_data_accept_2, telegram_message_fetch_data_accept_3, redeem_new_token_check, \
    redeem_new_token, redeem_new_token_callback_check, message_is_acceptable_check, user_quote_limit_check, \
    user_has_active_plan_check, telegram_message_check, file_link_list_handler


sample_json_input = {'update_id': 186486961, 'message': {'message_id': 189, 'from': {'id': 69254432, 'is_bot': False, 'first_name': 'amir hossein', 'username': 'SHAHAB_1372', 'language_code': 'en'}, 'chat': {'id': 69254432, 'first_name': 'amir hossein', 'username': 'SHAHAB_1372', 'type': 'private'}, 'date': 1711274810, 'text': 'd'}}


def request_file_check():
    telegram_response_check_result = telegram_response_check(request, True)
    if not telegram_response_check_result:
        return JsonResponse({'message': 'telegram_response_has_error'})
    else:
        user_unique_id = telegram_response_check_result[0]
        user_first_name = telegram_response_check_result[1]
        message_text = telegram_response_check_result[2]
        user_phone_number = telegram_response_check_result[3]

    if not under_construction_check(user_unique_id, True):
        return JsonResponse({'message': 'under_construction_is_active'})

    try:
        user = User.objects.get(username=user_unique_id)
    except:
        if user_phone_number:
            user_phone_number = str(user_phone_number).replace('+', '')
            if check_user_phone_number_is_allowed_to_register(user_phone_number):
                user = User.objects.create_user(username=user_unique_id, first_name=user_first_name)
                profile = user.user_profile
                profile.user_telegram_phone_number = str(user_phone_number).replace('+', '')
                profile.save()
                telegram_message_start_first_time(user_unique_id)
                return JsonResponse({'message': 'telegram_message_start_first_time'})
            else:
                telegram_message_phone_number_is_not_allowed(user_unique_id)
                return JsonResponse({'message': 'telegram_message_phone_number_is_not_allowed'})
        else:
            telegram_message_confirm_phone_number_warning(user_unique_id)
            return JsonResponse({'message': 'telegram_message_confirm_phone_number_warning'})

    if message_text == '/start':
        telegram_message_start(user_unique_id)
        return JsonResponse({'message': 'telegram_message_start'})

    if message_text == "🔙 بازگشت":
        telegram_message_start(user_unique_id)
        return JsonResponse({'message': 'telegram_message_start'})

    if message_text == "🏡 صفحه اصلی":
        telegram_message_start(user_unique_id)
        return JsonResponse({'message': 'telegram_message_start'})

    if message_text == 'payment_term_agree_no':
        telegram_message_start(user_unique_id)
        return JsonResponse({'message': 'telegram_message_start'})

    if message_text == 'راهنمای دانلود':
        telegram_message_download_help(user_unique_id)
        return JsonResponse({'message': 'telegram_message_download_help'})

    if message_text == 'دانلود فایل':
        telegram_message_download_file(user_unique_id)
        return JsonResponse({'message': 'telegram_message_download_file'})

    if message_text == 'دانلود از Envato Elements':
        telegram_message_download_from_envato_elements(user_unique_id)
        return JsonResponse({'message': 'telegram_message_download_from_envato_elements'})

    if message_text == 'ورود به سایت':
        telegram_message_login(user_unique_id)
        return JsonResponse({'message': 'telegram_message_login'})

    if message_text == 'تغییر زبان':
        telegram_message_change_language(user_unique_id)
        return JsonResponse({'message': 'telegram_message_change_language'})

    if message_text == 'خرید عمده و همکاری':
        telegram_message_partnership(user_unique_id)
        return JsonResponse({'message': 'telegram_message_partnership'})

    if message_text == 'لیست دانلود ها':
        telegram_message_download_list(user_unique_id, user)
        return JsonResponse({'message': 'telegram_message_download_list'})

    if message_text == 'گزارش حسابداری':
        telegram_message_financial_report(user_unique_id, user)
        return JsonResponse({'message': 'telegram_message_financial_report'})

    if message_text == 'شارژ حساب':
        telegram_message_wallet_charge(user_unique_id)
        return JsonResponse({'message': 'telegram_message_wallet_charge'})

    if message_text == 'telegram_wallet_charge_callback_main_page':
        telegram_wallet_charge_callback_main_page(user_unique_id)
        return JsonResponse({'message': 'telegram_wallet_charge_callback_main_page'})

    if message_text == 'مشاهده موجودی':
        telegram_message_account_state(user_unique_id, user)
        return JsonResponse({'message': 'telegram_message_account_state'})

    if message_text == 'بخش پشتیبانی':
        telegram_message_support(user_unique_id)
        return JsonResponse({'message': 'telegram_message_support'})

    if message_text == 'support_callback_yes':
        telegram_message_support_callback_yes(user_unique_id)
        return JsonResponse({'message': 'telegram_message_support_callback_yes'})

    if message_text == 'support_callback_no':
        telegram_message_support_callback_no(user_unique_id)
        return JsonResponse({'message': 'telegram_message_support_callback_no'})

    if message_text == 'درباره':
        telegram_message_about(user_unique_id)
        return JsonResponse({'message': 'telegram_message_about'})

    if message_text == 'راهنما':
        telegram_message_help(user_unique_id)
        return JsonResponse({'message': 'telegram_message_help'})

    if message_text == 'پروفایل کاربری':
        telegram_message_profile_menu(user_unique_id)
        return JsonResponse({'message': 'telegram_message_profile_menu'})

    if message_text == 'fetch_data_accept_1':
        telegram_message_fetch_data_accept_1(user_unique_id, user)
        return JsonResponse({'message': 'telegram_message_fetch_data_accept_1'})

    if message_text == 'fetch_data_accept_2':
        telegram_message_fetch_data_accept_2(user_unique_id, user)
        return JsonResponse({'message': 'telegram_message_fetch_data_accept_2'})

    if message_text == 'fetch_data_accept_3':
        telegram_message_fetch_data_accept_3(user_unique_id, user)
        return JsonResponse({'message': 'telegram_message_fetch_data_accept_3'})

    if redeem_new_token_check(message_text):
        redeem_new_token(message_text, user, user_unique_id)
        return JsonResponse({'message': 'redeem_new_token'})

    if redeem_new_token_callback_check(message_text):
        message_text = str(message_text)
        message_text = message_text.replace('redeem_callback_yes_', '')
        redeem_new_token(message_text, user, user_unique_id)

    if not message_is_acceptable_check(message_text, user_unique_id, True):
        return JsonResponse({'message': 'message_is_not_acceptable'})

    if not user_quote_limit_check(message_text, user_unique_id, user, True):
        return JsonResponse({'message': 'user_quote_limit_is_reached'})

    if not user_has_active_plan_check(user_unique_id, user, True):
        return JsonResponse({'message': 'user_has_no_active_plan'})

    telegram_message_check_result = telegram_message_check(message_text, user_unique_id, True)
    if not telegram_message_check_result:
        return JsonResponse({'message': 'telegram_message_unknown'})

    file_link_list_handler(user_unique_id, user, telegram_message_check_result)
    return JsonResponse({'message': 'file_link_list_handled'})
