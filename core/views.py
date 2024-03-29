import json
import threading
import time
import re
from decimal import Decimal

import jdatetime
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.views import View
from accounts.models import UserRequestHistory, UserRequestHistoryDetail, UserScraperTokenRedeemHistory, UserMultiToken, \
    user_wallet_charge, create_user_multi_token, WalletRedeemToken, ScraperRedeemToken, UserWalletChargeHistory
from core.models import get_core_settings, File, AriaCode, RequestDetail
from core.tasks import ScrapersMainFunctionThread
from maxim_telegram_bot.settings import BASE_URL
from utilities.telegram_message_handler import telegram_http_send_message_via_get_method, \
    telegram_http_send_message_via_post_method
from custom_logs.models import custom_log


def scrapers_start_view(request):
    if request.user.is_authenticated and request.user.is_superuser:
        if request.method == 'GET':
            ScrapersMainFunctionThread(name='scrapers_main_function_thread').start()
            return JsonResponse({'message': 'envato_scraper: scraper has been started'})
        else:
            return JsonResponse({'message': 'not allowed'})
    else:
        return JsonResponse({'message': 'not allowed'})


class RequestFile(View):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.context = {'detail': 'ثبت نام کاربر جدید'}
        self.today = jdatetime.datetime.now()

    def get(self, request, *args, **kwargs):
        return JsonResponse({'message': 'not allowed'})

    def post(self, request, *args, **kwargs):
        try:
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
            except Exception as e:
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
                telegram_message_account_state(user)
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

            # if message_text == 'fetch_data_accept_1':
            #     telegram_message_fetch_data_accept_1(user_unique_id, user)
            #     return JsonResponse({'message': 'telegram_message_fetch_data_accept_1'})
            #
            # if message_text == 'fetch_data_accept_2':
            #     telegram_message_fetch_data_accept_2(user_unique_id, user)
            #     return JsonResponse({'message': 'telegram_message_fetch_data_accept_2'})
            #
            # if message_text == 'fetch_data_accept_3':
            #     telegram_message_fetch_data_accept_3(user_unique_id, user)
            #     return JsonResponse({'message': 'telegram_message_fetch_data_accept_3'})

            if redeem_new_token_check(message_text):
                redeem_new_token_send_detail_message_to_telegram(user, message_text)
                return JsonResponse({'message': 'redeem_new_token'})

            if redeem_new_token_callback_check(message_text):
                redeem_new_token_after_callback(user, message_text)
                return JsonResponse({'message': 'redeem_new_token_after_callback'})

            if not message_is_acceptable_check(message_text, user_unique_id, True):
                return JsonResponse({'message': 'message_is_not_acceptable'})

            if process_links_and_apply_charge_check(message_text):
                process_links_and_apply_charge(user, message_text)
                return JsonResponse({'message': 'process_links_and_apply_charge'})

            # if not user_has_active_plan_check(user_unique_id, user, True):
            #     return JsonResponse({'message': 'user_has_no_active_plan'})

            telegram_message_check_result = telegram_message_check(message_text, user_unique_id, True)
            if not telegram_message_check_result:
                return JsonResponse({'message': 'telegram_message_unknown'})

            process_links_and_send_message_to_telegram(user, telegram_message_check_result)
            return JsonResponse({'message': 'process_links_and_send_message_to_telegram'})

        except Exception as e:
            custom_log(f'{e}')
            return JsonResponse({'message': f'{e}'})


class RequestHandler(threading.Thread):
    def __init__(self, user, file_page_link_list, data_track):
        super().__init__()
        self.user = user
        self.file_page_link_list = file_page_link_list
        self.data_track = data_track

    def run(self):
        try:
            new_user_request_history = UserRequestHistory.objects.create(user=self.user,
                                                                         data_track=self.data_track)
            text = f'''موارد زیر توسط ربات تایید و درحال بررسی می باشند: \n\n'''
            for file_page_link in self.file_page_link_list:
                try:
                    file_type = file_page_link[0]
                    link = file_page_link[1]
                    file_unique_code = file_page_link[2]
                    try:
                        file = File.objects.get(file_type=file_type, unique_code=file_unique_code)
                        if not file.is_acceptable_file and not file.in_progress and file.failed_repeat == 10:
                            file.is_acceptable_file = True
                            file.failed_repeat = 0
                            file.save()
                        else:
                            pass
                    except:
                        file = File.objects.create(file_type=file_type, page_link=link, unique_code=file_unique_code)
                    if file_type == 'envato':
                        text += f'سرویس دهنده: EnvatoElement'
                    if file_type == 'motion_array':
                        text += f'سرویس دهنده: MotionArray'
                    text += f'\n'
                    text += f'کد 🔁: {file_unique_code}'
                    text += f'\n'
                    text += f'____________________'
                    text += f'\n\n'
                    new_user_request_history.files.add(file)
                    new_user_request_history.save()
                except Exception as e:
                    custom_log('RequestHandler->forloop try/except. err: ' + str(e))
            text += f'🔷🔶🔶🔶🔶🔶🔶🔷'
            text += f'\n\n'
            telegram_response = telegram_http_send_message_via_post_method(chat_id=self.user, text=text,
                                                                           parse_mode='HTML')
            response = json.loads(telegram_response['message'])
            message_id = response['result']['message_id']
            chat_id = response['result']['chat']['id']
            UserRequestHistoryDetail.objects.create(
                user_request_history=new_user_request_history,
                telegram_chat_id=chat_id,
                telegram_message_id=message_id,
            )
        except Exception as e:
            custom_log('RequestHandler->try/except. err: ' + str(e))
        return


def telegram_response_check(request, custom_log_print: bool):
    try:
        secret_key = request.META['HTTP_X_TELEGRAM_BOT_API_SECRET_TOKEN']
        if secret_key is not None and str(secret_key) == '12587KFlk54NCJDmvn8541':
            if custom_log_print:
                custom_log('secret_key: confirmed')
            try:
                front_input = json.loads(request.body)
                if custom_log_print:
                    custom_log(str(front_input))
                try:
                    try:
                        user_unique_id = front_input['callback_query']['from']['id']
                        user_first_name = front_input['callback_query']['from']['first_name']
                        message_text = front_input['callback_query']['data']
                        response_list = [user_unique_id, user_first_name, message_text, None]
                    except:
                        try:
                            user_unique_id = front_input['message']['from']['id']
                            user_first_name = front_input['message']['from']['first_name']
                            message_text = str(front_input['message']['text'])
                            response_list = [user_unique_id, user_first_name, message_text, None]
                        except:
                            user_unique_id = front_input['message']['contact']['user_id']
                            user_first_name = front_input['message']['contact']['first_name']
                            message_text = str(front_input['message']['reply_to_message']['text'])
                            user_phone_number = front_input['message']['contact']['phone_number']
                            response_list = [user_unique_id, user_first_name, message_text, user_phone_number]
                    return response_list
                except Exception as e:
                    if custom_log_print:
                        custom_log('RequestFile->try/except. err: ' + str(e))
                    return False
            except:
                if custom_log_print:
                    custom_log('input format is not correct')
                return False
        else:
            if custom_log_print:
                custom_log('wrong secret_key')
            return False
    except:
        if custom_log_print:
            custom_log('unauthorized access')
        return False


def under_construction_check(user_unique_id, custom_log_print: bool):
    # check if core settings under construction is active
    if get_core_settings().service_under_construction:
        message_text = 'ربات در حال حاضر قادر به خدمات دهی نمی باشد'
        telegram_http_send_message_via_post_method(chat_id=user_unique_id, text=message_text, parse_mode='HTML')
        time.sleep(1)
        if custom_log_print:
            custom_log('service core setting *under construction* is active')
        return False
    else:
        return True


def check_user_phone_number_is_allowed_to_register(phone_number):
    try:
        aria_codes = AriaCode.objects.all()
        settings = get_core_settings()
        if settings.aria_code_acceptance == 'همه به جز':
            for aria_code in aria_codes:
                if phone_number.startswith(f'{aria_code.aria_code}'):
                    return False
            return True
        else:
            for aria_code in aria_codes:
                if phone_number.startswith(f'{aria_code.aria_code}'):
                    return True
            return False
    except Exception as e:
        custom_log(f'{e}')
        return False


def telegram_message_start_first_time(user_unique_id):
    # Define the menu buttons
    menu_buttons = [
        ["راهنمای دانلود", "دانلود فایل"],
        ["شارژ حساب", "پروفایل کاربری"]
    ]

    # Create the keyboard markup
    keyboard_markup = {
        "keyboard": menu_buttons,
        "resize_keyboard": True,
        "one_time_keyboard": True
    }

    # Convert the markup to a JSON string
    reply_markup = json.dumps(keyboard_markup)

    message_text = "ثبت نام شما با موفقیت انجام شد. \n به ربات تلگرام مکسیمم شاپ خوش آمدید. در این ربات می توانید فایل های دلخواه خود را از برترین سایت های دنیا به سادگی چند کلیک دانلود نمایید."
    telegram_http_send_message_via_post_method(chat_id=user_unique_id, text=message_text,
                                               reply_markup=reply_markup, parse_mode='Markdown')


def telegram_message_phone_number_is_not_allowed(user_unique_id):
    message_text = "شماره ارائه شده در حال حاضر قادر به استفاده از خدمات ما نمی باشد."
    telegram_http_send_message_via_post_method(chat_id=user_unique_id, text=message_text, parse_mode='HTML')


def telegram_message_start(user_unique_id):
    # Define the menu buttons
    menu_buttons = [
        ["راهنمای دانلود", "دانلود فایل"],
        ["شارژ حساب", "پروفایل کاربری"]
    ]

    # Create the keyboard markup
    keyboard_markup = {
        "keyboard": menu_buttons,
        "resize_keyboard": True,
        "one_time_keyboard": True
    }

    # Convert the markup to a JSON string
    reply_markup = json.dumps(keyboard_markup)

    message_text = "صفحه اصلی"
    telegram_http_send_message_via_post_method(chat_id=user_unique_id, text=message_text,
                                               reply_markup=reply_markup, parse_mode='Markdown')


def telegram_message_confirm_phone_number_warning(user_unique_id):
    reply_markup = {'keyboard': [
        [
            {'text': 'تایید شماره تلفن',
             'request_contact': True
             }
        ]
    ],
        'one_time_keyboard': True
    }

    reply_markup = json.dumps(reply_markup)

    message_text = "برای تایید عضویت لازم هست دکمه تایید شماره تلفن را انتخاب نمایید"
    telegram_http_send_message_via_post_method(chat_id=user_unique_id, text=message_text,
                                               reply_markup=reply_markup, parse_mode='Markdown')


def telegram_message_download_help(user_unique_id):
    message_text = f'''
                    لطفاً جهت دانلود از سایت <a href="https://www.uplooder.net/img/image/61/88597ff6b31d3f78134a9ce2c5dc67b2/help1.png">Envato Elements</a> همانند تصویر زیر لینک فایل مورد نظر را کپی کرده و در ربات وارد کنید. \n لینک های مورد نظر را میتوانید بصورت تک به تک و یا در یک پیام (هر لینک در یک خط) ارسال کنید. \n توجه داشته باشید که پس از ارسال لینک ربات بصورت خودکار شروع به دانلود فایل مورد نظر خواهد کرد. به همین جهت در صورت ارسال لینک و یا کد اشتباه مبلغ حساب شما عودت داده نمی شود.
                    '''
    telegram_http_send_message_via_post_method(chat_id=user_unique_id, text=message_text,
                                               parse_mode='HTML')


def telegram_message_download_file(user_unique_id):
    menu_buttons = [
        ["دانلود از Envato Elements"],
        ["🏡 صفحه اصلی", "🔙 بازگشت"],
    ]
    keyboard_markup = {
        "keyboard": menu_buttons,
        "resize_keyboard": True,
        "one_time_keyboard": True
    }
    reply_markup = json.dumps(keyboard_markup)

    message_text = "منوی دانلود فایل"
    telegram_http_send_message_via_post_method(chat_id=user_unique_id, text=message_text,
                                               reply_markup=reply_markup, parse_mode='Markdown')


def telegram_message_download_from_envato_elements(user_unique_id):
    message_text = f'''
            لطفاً جهت دانلود از سایت <a href="https://www.uplooder.net/img/image/61/88597ff6b31d3f78134a9ce2c5dc67b2/help1.png">Envato Elements</a> همانند تصویر زیر لینک فایل مورد نظر را کپی کرده و در ربات وارد کنید. \n لینک های مورد نظر را میتوانید بصورت تک به تک و یا در یک پیام (هر لینک در یک خط) ارسال کنید. \n توجه داشته باشید که پس از ارسال لینک ربات بصورت خودکار شروع به دانلود فایل مورد نظر خواهد کرد. به همین جهت در صورت ارسال لینک و یا کد اشتباه مبلغ حساب شما عودت داده نمی شود.
            '''
    telegram_http_send_message_via_post_method(chat_id=user_unique_id, text=message_text,
                                               parse_mode='HTML')


def telegram_message_login(user_unique_id):
    message_text = f'''
            <a href="https://maxish.ir/">جهت مشاهده سایت و محصولات دیگر گروه مکسیموم شاپ کلیک کنید</a> 
            '''
    telegram_http_send_message_via_post_method(chat_id=user_unique_id, text=message_text,
                                               parse_mode='HTML')


def telegram_message_change_language(user_unique_id):
    message_text = f'''
               با عرض پوزش در حال حاضر این مورد غیر فعال میباشد و طی آپدیت های بعدی ربات، منو زبان انگلیسی افزوده خواهد شد. 
               '''
    telegram_http_send_message_via_post_method(chat_id=user_unique_id, text=message_text,
                                               parse_mode='HTML')


def telegram_message_partnership(user_unique_id):
    message_text = f'''
                ربات مکسیموم شاپ در خصوصی کابران و همکارانی که خرید با تعداد بالا دارد بسته های اختصاصی را قرار داده است که کاربران می توانند با خرید این بسته های مقرون بصرفه شروع با فایل های خود کنند. \n در صورت پشتیبانی مستقیم و ایجاد ارتباط با آیدی زیر در ارتباط باشید. \n <a href="https://t.me/Maximum_S">https://t.me/Maximum_S</a>
                '''
    telegram_http_send_message_via_post_method(chat_id=user_unique_id, text=message_text,
                                               parse_mode='HTML')


def telegram_message_download_list(user_unique_id, user):
    user_requests_history = UserRequestHistory.objects.filter(user=user)
    user_download_list = []
    for user_request_history in user_requests_history:
        for envato_file in user_request_history.files.all():
            user_download_list.append(envato_file)
    user_request_history = list(set(user_download_list))

    now = jdatetime.datetime.now()
    finished_request_successful_list = []
    for file in user_request_history:
        if file.download_percentage == 100:
            difference = now - file.created_at
            if difference.total_seconds() < 24 * 3600:
                finished_request_successful_list.append(file)
        elif file.is_acceptable_file and file.in_progress and file.failed_repeat != 10:
            pass
            # text += f'⬇️{i}- EnvatoElement_{file.unique_code} - <b>در حال دانلود</b>'
            # text += '\n'
        else:
            pass
            # text += f'⬇️{i}- EnvatoElement_{file.unique_code} - <b>خطای دانلود</b>'
            # text += '\n'
    text = f''''''
    if len(finished_request_successful_list) == 0:
        text = 'شما در 24 ساعت گذشته دانلودی نداشته اید'
    else:
        text += 'تاریخچه دانلود شما در 24 ساعت گذشته به شرح ذیل می باشد: '
        text += '\n'
        i = 0
        for file in finished_request_successful_list:
            if file.download_percentage == 100:
                if file.file:
                    text += f'⬇️{i}- EnvatoElement_{file.unique_code} - <a href="{BASE_URL}{file.file.url}">لینک دانلود</a>'
                else:
                    text += f'⬇️{i}- EnvatoElement_{file.unique_code} - لینک غیر فعال'
                text += '\n'
                i += 1
    telegram_http_send_message_via_post_method(chat_id=user_unique_id, text=text,
                                               parse_mode='HTML')


def telegram_message_financial_report(user_unique_id, user):
    today = jdatetime.datetime.now()
    user_redeems_history = UserScraperTokenRedeemHistory.objects.filter(user=user)
    text = f''''''
    if user_redeems_history.count() == 0:
        text = 'تا کنون خدماتی نداشتید'
    else:
        i = 1
        for user_redeem_history in user_redeems_history:
            try:
                if i % 2 == 0:
                    color = '🟥'
                else:
                    color = '🟩'
                if user_redeem_history.redeemed_token.token_name:
                    text += f'{color}{i}- {user_redeem_history.redeemed_token.token_name}'
                else:
                    if user_redeem_history.redeemed_token.token_type == 'single':
                        text += f'{color}{i}- بسته {user_redeem_history.redeemed_token.tokens_count} عددی با انقضای {user_redeem_history.redeemed_token.expiry_days} روزه'
                    else:
                        text += f'{color}{i}بسته روزانه {user_redeem_history.redeemed_token.tokens_count} عددی با انقضای {user_redeem_history.redeemed_token.expiry_days} روزه'
                text += f'\n'
                text += f'کد یکتا: {user_redeem_history.redeemed_token.token_unique_code}'
                text += f'\n'
                text += f'ردیم شده در: {user_redeem_history.created_at.strftime("%Y/%m/%d %H:%M")}'
                text += f'\n'
                if (user_redeem_history.created_at + jdatetime.timedelta(
                        days=user_redeem_history.redeemed_token.expiry_days)) > today:
                    text += f'قابل استفاده تا: {(user_redeem_history.created_at + jdatetime.timedelta(days=user_redeem_history.redeemed_token.expiry_days)).strftime("%Y/%m/%d %H:%M")}'
                    text += f'\n\n'
                else:
                    text += f'منقضی شده'
                    text += f'\n\n'
                i += 1
            except:
                pass
    telegram_http_send_message_via_post_method(chat_id=user_unique_id, text=text,
                                               parse_mode='HTML')


def telegram_message_wallet_charge(user_unique_id):
    inline_keyboard = [
        [
            {"text": "Envato Elements",
             "url": "https://maxish.ir"},
            {"text": "MotionArray",
             "url": "https://maxish.ir"}
        ],
        [
            {"text": "صفحه اصلی",
             "callback_data": "telegram_wallet_charge_callback_main_page"}
        ]
    ]

    keyboard_markup = {
        "inline_keyboard": inline_keyboard
    }

    support_reply_markup = json.dumps(keyboard_markup)

    message_text = f''''''
    message_text += 'برای خرید لایسنس سرویس مورد نظر خود وارد صفحه محصول مرتبط شوید.'
    message_text += '\n'
    message_text += 'نحوه وارد کردن لایسنس و ضریب کسر اعتبار هر سرویس در صفحه هر محصول درج شده و همچنین بعد از خرید موارد مجدد ارسال خواهد شد.'
    message_text += '\n'
    telegram_http_send_message_via_post_method(chat_id=user_unique_id, text=message_text,
                                               reply_markup=support_reply_markup, parse_mode='Markdown')


def telegram_wallet_charge_callback_main_page(user_unique_id):
    menu_buttons = [
        ["راهنمای دانلود", "دانلود فایل"],
        ["شارژ حساب", "پروفایل کاربری"]
    ]

    # Create the keyboard markup
    keyboard_markup = {
        "keyboard": menu_buttons,
        "resize_keyboard": True,
        "one_time_keyboard": True
    }

    # Convert the markup to a JSON string
    reply_markup = json.dumps(keyboard_markup)

    message_text = "صفحه اصلی"
    telegram_http_send_message_via_post_method(chat_id=user_unique_id, text=message_text,
                                               reply_markup=reply_markup, parse_mode='Markdown')


def telegram_message_account_state(user):
    account_state_markup = json.dumps(
        {"inline_keyboard": [[{"text": "صفحه اصلی", "callback_data": "🏡 صفحه اصلی"}]]})

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
    if en_has_active_token:
        message += f'🟩 بسته دانلود انواتو'
        message += f'\n'
        message += f'<b>⌛تاریخ انقضا بسته: {en_expiry_date}</b>'
        message += f'\n'
        message += f'<b>تعداد مصرف شده در 24 ساعت: {en_daily_allowed_number - en_daily_remaining_tokens} از {en_daily_allowed_number}</b>'
        message += f'\n'
        message += f'(محدودیت دانلود هر 24 ساعت ریست می شود)'
        message += f'\n'
        message += f'<b>تعداد مصرف شده کل: {en_total_tokens - en_total_remaining_tokens} از {en_total_tokens}</b>'
        message += f'\n'
        message += f'--------'
        message += f'\n\n'

    if ma_has_active_token:
        message += f'🟦 بسته دانلود موشن ارای'
        message += f'\n'
        message += f'<b>⌛تاریخ انقضا بسته: {ma_expiry_date}</b>'
        message += f'\n'
        message += f'<b>تعداد مصرف شده در 24 ساعت: {ma_daily_allowed_number - ma_daily_remaining_tokens} از {ma_daily_allowed_number}</b>'
        message += f'\n'
        message += f'(محدودیت دانلود هر 24 ساعت ریست می شود)'
        message += f'\n'
        message += f'<b>تعداد مصرف شده کل: {ma_total_tokens - ma_total_remaining_tokens} از {ma_total_tokens}</b>'
        message += f'\n'
        message += f'--------'
        message += f'\n\n'

    message += f'⭐ موجودی اعتبار حساب: {w_cr}'
    message += '\n'
    telegram_http_send_message_via_post_method(chat_id=user.username, reply_markup=account_state_markup, text=message,
                                               parse_mode='HTML')


def telegram_message_account_state_as_message(user):
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
    if en_has_active_token:
        message += f'🟩 بسته دانلود انواتو'
        message += f'\n'
        message += f'<b>⌛تاریخ انقضا بسته: {en_expiry_date}</b>'
        message += f'\n'
        message += f'<b>تعداد مصرف شده در 24 ساعت: {en_daily_allowed_number - en_daily_remaining_tokens} از {en_daily_allowed_number}</b>'
        message += f'\n'
        message += f'(محدودیت دانلود هر 24 ساعت ریست می شود)'
        message += f'\n'
        message += f'<b>تعداد مصرف شده کل: {en_total_tokens - en_total_remaining_tokens} از {en_total_tokens}</b>'
        message += f'\n'
        message += f'--------'
        message += f'\n\n'

    if ma_has_active_token:
        message += f'🟦 بسته دانلود موشن ارای'
        message += f'\n'
        message += f'<b>⌛تاریخ انقضا بسته: {ma_expiry_date}</b>'
        message += f'\n'
        message += f'<b>تعداد مصرف شده در 24 ساعت: {ma_daily_allowed_number - ma_daily_remaining_tokens} از {ma_daily_allowed_number}</b>'
        message += f'\n'
        message += f'(محدودیت دانلود هر 24 ساعت ریست می شود)'
        message += f'\n'
        message += f'<b>تعداد مصرف شده کل: {ma_total_tokens - ma_total_remaining_tokens} از {ma_total_tokens}</b>'
        message += f'\n'
        message += f'--------'
        message += f'\n\n'

    message += f'⭐ موجودی اعتبار حساب: {w_cr}'
    message += '\n'
    return message


def telegram_message_support(user_unique_id):
    inline_keyboard = [
        [
            {"text": "بله",
             "callback_data": "support_callback_yes"},
            {"text": "خیر",
             "callback_data": "🏡 صفحه اصلی"}
        ],
        [
            {"text": "صفحه اصلی",
             "callback_data": "🏡 صفحه اصلی"}
        ]
    ]

    keyboard_markup = {
        "inline_keyboard": inline_keyboard
    }

    support_reply_markup = json.dumps(keyboard_markup)

    message_text = "آیا سوالی دارید؟"
    telegram_http_send_message_via_post_method(chat_id=user_unique_id, text=message_text,
                                               reply_markup=support_reply_markup, parse_mode='Markdown')


def telegram_message_support_callback_yes(user_unique_id):
    message_text = f'جهت ارتباط با پشتیبانی با ایدی زیر در ارتباط باشید'
    message_text += '\n\n'
    message_text += 'https://t.me/Maximum_S'
    telegram_http_send_message_via_post_method(chat_id=user_unique_id, text=message_text, parse_mode='HTML')


def telegram_message_support_callback_no(user_unique_id):
    pass


def telegram_message_about(user_unique_id):
    message_text = f'''
                درباره
                '''
    telegram_http_send_message_via_post_method(chat_id=user_unique_id, text=message_text,
                                               parse_mode='HTML')


def telegram_message_help(user_unique_id):
    message_text = f'''
                راهنما
                '''
    telegram_http_send_message_via_post_method(chat_id=user_unique_id, text=message_text,
                                               parse_mode='HTML')


def telegram_message_profile_menu(user_unique_id):
    menu_buttons = [
        ['تغییر زبان', 'مشاهده موجودی', 'شارژ حساب'],
        ['گزارش حسابداری', 'لیست دانلود ها', 'بخش پشتیبانی'],
        ["🏡 صفحه اصلی", "🔙 بازگشت"],
    ]
    keyboard_markup = {
        "keyboard": menu_buttons,
        "resize_keyboard": True,
        "one_time_keyboard": True
    }
    reply_markup = json.dumps(keyboard_markup)

    message_text = "منوی پروفایل کاربری"
    telegram_http_send_message_via_post_method(chat_id=user_unique_id, text=message_text,
                                               reply_markup=reply_markup, parse_mode='Markdown')


def redeem_new_token_check(message_text):
    message_text = str(message_text)
    message_text = message_text.replace('Envato-', '')
    message_text = message_text.replace('Motion-', '')
    if len(str(message_text)) == 19 and str(message_text)[4] == '-' and str(message_text)[9] == '-' and \
            str(message_text)[14] == '-':
        return True
    else:
        return False


def check_input_token(user, token_type, token_unique_code):
    if token_type == 'wallet':
        try:
            wallet_redeem_token = WalletRedeemToken.objects.get(token_unique_code=token_unique_code)
            if not wallet_redeem_token.is_used:
                response = {
                    'token_exist_id_db': True,
                    'token_is_used': False,
                    'token_unique_code': token_unique_code,
                    'token_charge_amount': wallet_redeem_token.charge_amount,

                }
            else:
                response = {
                    'token_exist_id_db': True,
                    'token_is_used': True,
                    'token_unique_code': token_unique_code,
                    'token_charge_amount': None
                }
        except:
            response = {
                'token_exist_id_db': False,
                'token_is_used': None,
                'token_unique_code': token_unique_code,
                'token_charge_amount': None
            }
    else:
        try:
            scraper_redeem_token = ScraperRedeemToken.objects.get(token_unique_code=token_unique_code)
            if not scraper_redeem_token.is_used:
                response = {
                    'token_exist_id_db': True,
                    'token_is_used': False,
                    'token_unique_code': token_unique_code,
                    'total_tokens': scraper_redeem_token.total_tokens,
                    'daily_allowed_number': scraper_redeem_token.daily_allowed_number,
                    'expiry_days': scraper_redeem_token.expiry_days,
                }
            else:
                response = {
                    'token_exist_id_db': True,
                    'token_is_used': True,
                    'token_unique_code': token_unique_code,
                    'total_tokens': scraper_redeem_token.total_tokens,
                    'daily_allowed_number': scraper_redeem_token.daily_allowed_number,
                    'expiry_days': scraper_redeem_token.expiry_days,
                }
        except:
            response = {
                'token_exist_id_db': False,
                'token_is_used': None,
                'token_unique_code': token_unique_code,
                'total_tokens': None,
                'daily_allowed_number': None,
                'expiry_days': None,
            }
    return response


def redeem_new_token_send_detail_message_to_telegram(user, message_text):
    new_token_unique_code = str(message_text)
    user_financial_state_result = user_financial_state(user)

    en_has_active_token = user_financial_state_result['user_envato_state']['has_active_token']
    ma_has_active_token = user_financial_state_result['user_motion_array_state']['has_active_token']

    en_total_tokens = user_financial_state_result['user_envato_state']['total_tokens']
    en_daily_allowed_number = user_financial_state_result['user_envato_state']['daily_allowed_number']
    en_expiry_date = user_financial_state_result['user_envato_state']['expiry_date']
    en_expiry_days = user_financial_state_result['user_envato_state']['expiry_days']

    ma_total_tokens = user_financial_state_result['user_motion_array_state']['total_tokens']
    ma_daily_allowed_number = user_financial_state_result['user_motion_array_state']['daily_allowed_number']
    ma_expiry_date = user_financial_state_result['user_motion_array_state']['expiry_date']
    ma_expiry_days = user_financial_state_result['user_motion_array_state']['expiry_days']

    message = f''''''
    if new_token_unique_code.find('Envato-') != -1:
        if en_has_active_token:
            redeem_new_token_markup = json.dumps(
                {"inline_keyboard": [[{"text": "صفحه اصلی", "callback_data": "🏡 صفحه اصلی"}]]})
            message = f'"بسته اشتراک انواتو - {en_total_tokens} دانلود – {en_expiry_days} روزه" با سقف دانلود " دانلود – {en_daily_allowed_number} عدد در روز " تا تاریخ {en_expiry_date} فعال است.'
            message += '\n'
            message += 'امکان ثبت بسته جدید از این نوع ندارید. در صورت مواجه شدن با محدودیت دانلود روزانه در بسته فعلی می توانید با خرید اعتبار حساب دانلود های خود را انجام دهید.'
            message += '\n'
            message += 'همچنین لایسنس وارد شده را بعد از اتمام بسته فعلی خود می توانید استفاده کنید.'
            telegram_http_send_message_via_post_method(chat_id=user.username, text=message,
                                                       reply_markup=redeem_new_token_markup, parse_mode='Markdown')
        else:
            check_input_token_result = check_input_token(user, 'envato', new_token_unique_code)
            token_exist_id_db = check_input_token_result['token_exist_id_db']
            token_is_used = check_input_token_result['token_is_used']
            token_unique_code = check_input_token_result['token_unique_code']
            total_tokens = check_input_token_result['total_tokens']
            daily_allowed_number = check_input_token_result['daily_allowed_number']
            expiry_days = check_input_token_result['expiry_days']
            if token_exist_id_db:
                if not token_is_used:
                    inline_keyboard = [
                        [
                            {"text": "بله",
                             "callback_data": f"redeem_callback_yes_{new_token_unique_code}"},
                            {"text": "خیر",
                             "callback_data": "🏡 صفحه اصلی"}
                        ],
                        [
                            {"text": "صفحه اصلی",
                             "callback_data": "🏡 صفحه اصلی"}
                        ]
                    ]

                    keyboard_markup = {
                        "inline_keyboard": inline_keyboard
                    }

                    redeem_new_token_markup = json.dumps(keyboard_markup)

                    message = f'شما در حال فعال سازی "بسته اشتراک انواتو – {total_tokens} دانلود – {expiry_days} روزه " با سقف دانلود " {daily_allowed_number} عدد  در روز" می باشید.'
                    message += '\n'
                    message += f'تاریخ انقضا این بسته بعد از فعال سازی {expiry_days} روز خواهد بود.'
                    message += '\n'
                    message += 'در صورت داشتن اعتبار و همچنین بسته اشتراکی، اولویت با بسته اشتراکی خواهد بود و از اعتبار حساب شما کاسته نخواهد شد.'
                    message += '\n'
                    message += 'فعال شود؟'

                    telegram_http_send_message_via_post_method(chat_id=user.username, text=message,
                                                               reply_markup=redeem_new_token_markup,
                                                               parse_mode='Markdown')
                else:
                    redeem_new_token_markup = json.dumps(
                        {"inline_keyboard": [[{"text": "صفحه اصلی", "callback_data": "🏡 صفحه اصلی"}]]})
                    message += f'توکن درخواستی با کد {token_unique_code} قبلا استفاده شده است'
                    telegram_http_send_message_via_post_method(chat_id=user.username, text=message,
                                                               reply_markup=redeem_new_token_markup,
                                                               parse_mode='Markdown')
            else:
                redeem_new_token_markup = json.dumps(
                    {"inline_keyboard": [[{"text": "صفحه اصلی", "callback_data": "🏡 صفحه اصلی"}]]})
                message += f'توکن درخواستی با کد {token_unique_code} اشتباه می باشد'
                telegram_http_send_message_via_post_method(chat_id=user.username, text=message,
                                                           reply_markup=redeem_new_token_markup, parse_mode='Markdown')

    elif new_token_unique_code.find('Motion-') != -1:
        if ma_has_active_token:
            redeem_new_token_markup = json.dumps(
                {"inline_keyboard": [[{"text": "صفحه اصلی", "callback_data": "🏡 صفحه اصلی"}]]})
            message = f'"بسته اشتراک موشن ارای - {ma_total_tokens} دانلود – {ma_expiry_days} روزه" با سقف دانلود " دانلود – {ma_daily_allowed_number} عدد در روز " تا تاریخ {ma_expiry_date} فعال است.'
            message += '\n'
            message += 'امکان ثبت بسته جدید از این نوع ندارید. در صورت مواجه شدن با محدودیت دانلود روزانه در بسته فعلی می توانید با خرید اعتبار حساب دانلود های خود را انجام دهید.'
            message += '\n'
            message += 'همچنین لایسنس وارد شده را بعد از اتمام بسته فعلی خود می توانید استفاده کنید.'
            telegram_http_send_message_via_post_method(chat_id=user.username, text=message,
                                                       reply_markup=redeem_new_token_markup, parse_mode='Markdown')
        else:
            check_input_token_result = check_input_token(user, 'motion_array', new_token_unique_code)
            token_exist_id_db = check_input_token_result['token_exist_id_db']
            token_is_used = check_input_token_result['token_is_used']
            token_unique_code = check_input_token_result['token_unique_code']
            total_tokens = check_input_token_result['total_tokens']
            daily_allowed_number = check_input_token_result['daily_allowed_number']
            expiry_days = check_input_token_result['expiry_days']
            if token_exist_id_db:
                if not token_is_used:
                    inline_keyboard = [
                        [
                            {"text": "بله",
                             "callback_data": f"redeem_callback_yes_{new_token_unique_code}"},
                            {"text": "خیر",
                             "callback_data": "🏡 صفحه اصلی"}
                        ],
                        [
                            {"text": "صفحه اصلی",
                             "callback_data": "🏡 صفحه اصلی"}
                        ]
                    ]

                    keyboard_markup = {
                        "inline_keyboard": inline_keyboard
                    }

                    redeem_new_token_markup = json.dumps(keyboard_markup)

                    message = f'شما در حال فعال سازی "بسته اشتراک موشن ارای – {total_tokens} دانلود – {expiry_days} روزه " با سقف دانلود " {daily_allowed_number} عدد  در روز" می باشید.'
                    message += '\n'
                    message += f'تاریخ انقضا این بسته بعد از فعال سازی {expiry_days} روز خواهد بود.'
                    message += '\n'
                    message += 'در صورت داشتن اعتبار و همچنین بسته اشتراکی، اولویت با بسته اشتراکی خواهد بود و از اعتبار حساب شما کاسته نخواهد شد.'
                    message += '\n'
                    message += 'فعال شود؟'

                    telegram_http_send_message_via_post_method(chat_id=user.username, text=message,
                                                               reply_markup=redeem_new_token_markup,
                                                               parse_mode='Markdown')
                else:
                    redeem_new_token_markup = json.dumps(
                        {"inline_keyboard": [[{"text": "صفحه اصلی", "callback_data": "🏡 صفحه اصلی"}]]})
                    message += f'توکن درخواستی با کد {token_unique_code} قبلا استفاده شده است'
                    telegram_http_send_message_via_post_method(chat_id=user.username, text=message,
                                                               reply_markup=redeem_new_token_markup,
                                                               parse_mode='Markdown')
            else:
                redeem_new_token_markup = json.dumps(
                    {"inline_keyboard": [[{"text": "صفحه اصلی", "callback_data": "🏡 صفحه اصلی"}]]})
                message += f'توکن درخواستی با کد {token_unique_code} اشتباه می باشد'
                telegram_http_send_message_via_post_method(chat_id=user.username, text=message,
                                                           reply_markup=redeem_new_token_markup, parse_mode='Markdown')

    else:
        check_input_token_result = check_input_token(user, 'wallet', new_token_unique_code)
        token_exist_id_db = check_input_token_result['token_exist_id_db']
        token_is_used = check_input_token_result['token_is_used']
        token_unique_code = check_input_token_result['token_unique_code']
        token_charge_amount = check_input_token_result['token_charge_amount']
        if token_exist_id_db:
            if not token_is_used:
                inline_keyboard = [
                    [
                        {"text": "بله",
                         "callback_data": f"redeem_callback_yes_{new_token_unique_code}"},
                        {"text": "خیر",
                         "callback_data": "🏡 صفحه اصلی"}
                    ],
                    [
                        {"text": "صفحه اصلی",
                         "callback_data": "🏡 صفحه اصلی"}
                    ]
                ]

                keyboard_markup = {
                    "inline_keyboard": inline_keyboard
                }

                redeem_new_token_markup = json.dumps(keyboard_markup)

                message = f'شما در حال شارژ اعتبار حساب به میزان {token_charge_amount} هستید.'
                message += '\n'
                message += 'انجام شود؟'

                telegram_http_send_message_via_post_method(chat_id=user.username, text=message,
                                                           reply_markup=redeem_new_token_markup,
                                                           parse_mode='Markdown')
            else:
                redeem_new_token_markup = json.dumps(
                    {"inline_keyboard": [[{"text": "صفحه اصلی", "callback_data": "🏡 صفحه اصلی"}]]})
                message += f'توکن درخواستی با کد {token_unique_code} قبلا استفاده شده است'
                telegram_http_send_message_via_post_method(chat_id=user.username, text=message,
                                                           reply_markup=redeem_new_token_markup,
                                                           parse_mode='Markdown')
        else:
            redeem_new_token_markup = json.dumps(
                {"inline_keyboard": [[{"text": "صفحه اصلی", "callback_data": "🏡 صفحه اصلی"}]]})
            message += f'توکن درخواستی با کد {token_unique_code} اشتباه می باشد'
            telegram_http_send_message_via_post_method(chat_id=user.username, text=message,
                                                       reply_markup=redeem_new_token_markup, parse_mode='Markdown')


def redeem_new_token_callback_check(message_text):
    message_text = str(message_text)
    if message_text.find('redeem_callback_yes_') != -1:
        return True
    else:
        return False


def redeem_new_token_after_callback(user, message_text):
    message_text = str(message_text)
    redeem_new_token_markup = json.dumps(
        {"inline_keyboard": [[{"text": "صفحه اصلی", "callback_data": "🏡 صفحه اصلی"}]]})
    message = f''''''
    new_token_unique_code = message_text.replace('redeem_callback_yes_', '')
    if new_token_unique_code.find('Envato-') != -1:
        create_user_multi_token_result = create_user_multi_token(user, 'envato', new_token_unique_code)
        UserScraperTokenRedeemHistory.objects.create(user=user, redeemed_token=create_user_multi_token_result[2])
        message += f'توکن درخواستی با کد {new_token_unique_code} فعال گردید'
    elif new_token_unique_code.find('Motion-') != -1:
        create_user_multi_token_result = create_user_multi_token(user, 'motion_array', new_token_unique_code)
        UserScraperTokenRedeemHistory.objects.create(user=user, redeemed_token=create_user_multi_token_result[2])
        message += f'توکن درخواستی با کد {new_token_unique_code} فعال گردید'
    else:
        create_wallet_charge_result = user_wallet_charge(user, new_token_unique_code)
        UserWalletChargeHistory.objects.create(user=user, redeemed_token=create_wallet_charge_result[1])
        message += f'توکن درخواستی با کد {new_token_unique_code} فعال گردید'
    message += '\n\n'
    message += telegram_message_account_state_as_message(user)
    telegram_http_send_message_via_post_method(chat_id=user.username, text=message,
                                               reply_markup=redeem_new_token_markup, parse_mode='HTML')
    return JsonResponse({"message": "redeem_new_token_after_callback complete"})


def message_is_acceptable_check(message_text, user_unique_id, custom_log_print: bool):
    # check if received message is acceptable
    if len(str(message_text)) > 3000:
        text = 'طول پیام ورودی بیشتر از حد مجاز می باشد'
        telegram_http_send_message_via_get_method(chat_id=user_unique_id,
                                                  text=text)
        if custom_log_print:
            custom_log('طول پیام ورودی بیشتر از حد مجاز می باشد :file_page_links')
        return False
    else:
        return True


def telegram_message_check(message_text, user_unique_id, custom_log_print: bool):
    # extract link from received message
    file_page_links = message_text.split()
    file_page_link_list = []
    for file_page_link in file_page_links:
        if file_page_link.find('https://elements.envato.com') != -1:
            # get origin of url
            file_page_link = str(file_page_link)
            if file_page_link.find('https://elements.envato.com/de/') != -1:
                file_page_link = file_page_link.replace('/de/', '/')
            if file_page_link.find('https://elements.envato.com/es/') != -1:
                file_page_link = file_page_link.replace('/es/', '/')
            if file_page_link.find('https://elements.envato.com/fr/') != -1:
                file_page_link = file_page_link.replace('/fr/', '/')
            if file_page_link.find('https://elements.envato.com/pt-br/') != -1:
                file_page_link = file_page_link.replace('/pt-br/', '/')
            if file_page_link.find('https://elements.envato.com/ru/') != -1:
                file_page_link = file_page_link.replace('/ru/', '/')
            custom_log(file_page_link)
            file_page_link = file_page_link[file_page_link.find('https://'):]
            custom_log(file_page_link)
            slash_index = 0
            i = 0
            for char in file_page_link:
                if char == '/':
                    if slash_index == 3:
                        file_page_link = file_page_link[:i]
                        break
                    slash_index += 1
                i += 1
            j = 0
            if file_page_link.find('?') != -1:
                for char in file_page_link:
                    if char == '?':
                        file_page_link = file_page_link[:j]
                        break
                    j += 1
            file_page_link_word_list = file_page_link.split('-')
            unique_code = file_page_link_word_list[-1]
            unique_code_check = re.sub("[A-Z0-9]", '', unique_code)
            if len(unique_code_check) == 0:
                file_page_link = '-'.join(file_page_link_word_list)
                file_page_link_list.append(['envato', file_page_link, unique_code])
            else:
                pass
        elif file_page_link.find('https://motionarray.com/') != -1:
            file_page_link = str(file_page_link)
            if file_page_link.find('/?q=') != -1:
                file_page_link = file_page_link.split('?q=')[0]
            if file_page_link[-1] == '/':
                file_page_link = file_page_link[:-2]
            file_page_link = file_page_link.split('-')
            unique_code = file_page_link[-1]
            file_page_link = '-'.join(file_page_link)
            file_page_link = f'{file_page_link}/'
            file_page_link_list.append(['motion_array', file_page_link, unique_code])
        else:
            pass
    if len(file_page_link_list) != 0:
        return file_page_link_list
    else:
        if custom_log_print:
            custom_log('RequestFile-> مقدار وارد شده صحیح نمی باشد')
        text = 'مقدار وارد شده صحیح نمی باشد'
        telegram_http_send_message_via_post_method(chat_id=user_unique_id, text=text, parse_mode='HTML')
        return False


def process_links(user, file_page_link_list):
    number_of_motion_array_links = 0
    number_of_envato_links = 0
    for file_page_link in file_page_link_list:
        if file_page_link[0] == 'envato':
            number_of_envato_links += 1
        else:
            number_of_motion_array_links += 1
    en_token_can_handle_number = token_can_handel_number(user, 'envato', number_of_envato_links)
    ma_token_can_handle_number = token_can_handel_number(user, 'motion_array', number_of_motion_array_links)

    if number_of_envato_links == 0:
        number_of_handled_envato_links = 0
        number_of_unhandled_envato_links = 0
        en_token = False
    elif en_token_can_handle_number == number_of_envato_links:
        number_of_handled_envato_links = en_token_can_handle_number
        number_of_unhandled_envato_links = 0
        en_token = True
    else:
        if en_token_can_handle_number == 0:
            number_of_handled_envato_links = 0
            number_of_unhandled_envato_links = number_of_envato_links
            en_token = False
        else:
            number_of_handled_envato_links = en_token_can_handle_number
            number_of_unhandled_envato_links = number_of_envato_links - number_of_handled_envato_links
            en_token = True

    if number_of_motion_array_links == 0:
        number_of_handled_motion_array_links = 0
        number_of_unhandled_motion_array_links = 0
        ma_token = False
    elif ma_token_can_handle_number == number_of_motion_array_links:
        number_of_handled_motion_array_links = ma_token_can_handle_number
        number_of_unhandled_motion_array_links = 0
        ma_token = True
    else:
        if ma_token_can_handle_number == 0:
            number_of_handled_motion_array_links = 0
            number_of_unhandled_motion_array_links = number_of_motion_array_links
            ma_token = False
        else:
            number_of_handled_motion_array_links = ma_token_can_handle_number
            number_of_unhandled_motion_array_links = number_of_motion_array_links - ma_token_can_handle_number
            ma_token = True

    if number_of_unhandled_envato_links == 0 and number_of_unhandled_motion_array_links == 0:
        need_credit = False
    else:
        need_credit = True

    process_links_result = {
        'en_token': en_token,
        'number_of_envato_links': number_of_envato_links,
        'number_of_handled_envato_links': number_of_handled_envato_links,
        'number_of_unhandled_envato_links': number_of_unhandled_envato_links,
        'ma_token': ma_token,
        'number_of_motion_array_links': number_of_motion_array_links,
        'number_of_handled_motion_array_links': number_of_handled_motion_array_links,
        'number_of_unhandled_motion_array_links': number_of_unhandled_motion_array_links,
        'need_credit': need_credit,
        'user_credit_is_sufficient': user_credit_is_sufficient(user, number_of_unhandled_envato_links,
                                                               number_of_unhandled_motion_array_links),
    }

    return process_links_result


def process_links_and_send_message_to_telegram(user, file_page_link_list):
    process_links_results = process_links(user, file_page_link_list)

    en_link_number = process_links_results['number_of_envato_links']
    en_link_handled = process_links_results['number_of_handled_envato_links']
    en_link_unhandled = process_links_results['number_of_unhandled_envato_links']

    ma_link_number = process_links_results['number_of_motion_array_links']
    ma_link_handled = process_links_results['number_of_handled_motion_array_links']
    ma_link_unhandled = process_links_results['number_of_unhandled_motion_array_links']

    en_f = process_links_results['user_credit_is_sufficient']['en_cost_factor']
    ma_f = process_links_results['user_credit_is_sufficient']['ma_cost_factor']

    w_cr = process_links_results['user_credit_is_sufficient']['wallet_credit']

    total_credit_needed = process_links_results['user_credit_is_sufficient']['total_cost']
    en_links_costs = process_links_results['user_credit_is_sufficient']['en_links_costs']
    ma_links_costs = process_links_results['user_credit_is_sufficient']['ma_links_costs']

    callback_message_extra = f'{en_link_number}_{en_link_handled}_{en_link_unhandled}_{en_links_costs}_'
    callback_message_extra += f'{ma_link_number}_{ma_link_handled}_{ma_link_unhandled}_{ma_links_costs}'

    request_detail = RequestDetail.objects.create(
        user=user,
        file_page_link_list=json.dumps(file_page_link_list),
        process_links_results=callback_message_extra,
    )

    message = f'فهرست کد ها:'
    message += '\n'
    i = 0
    j = 0
    for file_page_link in file_page_link_list:
        if file_page_link[0] == 'motion_array':
            from_x = 'موشن ارای'
            message += f'🟢 کد: {file_page_link[2]} - از: {from_x}'
            message += '\n'
            i += 1
        else:
            from_x = 'انواتو'
            message += f'🔴 کد: {file_page_link[2]} - از: {from_x}'
            message += '\n'
            j += 1

    message += f'تعداد کل: {i + j}'
    message += '\n\n'

    if process_links_results['need_credit']:
        if process_links_results['en_token'] or process_links_results['ma_token']:
            message += f'🔵 موجودی اعتبار حساب: {w_cr}'
            message += '\n'
            user_financial_state_result = user_financial_state(user)
            if process_links_results['en_token']:
                total_remaining_tokens = user_financial_state_result['user_envato_state']['total_remaining_tokens']
                daily_remaining_tokens = user_financial_state_result['user_envato_state']['daily_remaining_tokens']
                total_tokens = user_financial_state_result['user_envato_state']['total_tokens']
                daily_allowed_number = user_financial_state_result['user_envato_state']['daily_allowed_number']
                expiry_date = user_financial_state_result['user_envato_state']['expiry_date']
                message += f'🔵 بسته انواتو: موجودی کل {total_tokens} - سقف استفاده روزانه {daily_allowed_number} - مانده کل {total_remaining_tokens} - مانده روزانه {daily_remaining_tokens} - انقضا در {expiry_date}'
                message += '\n'
            if process_links_results['ma_token']:
                total_remaining_tokens = user_financial_state_result['user_motion_array_state'][
                    'total_remaining_tokens']
                daily_remaining_tokens = user_financial_state_result['user_motion_array_state'][
                    'daily_remaining_tokens']
                total_tokens = user_financial_state_result['user_motion_array_state']['total_tokens']
                daily_allowed_number = user_financial_state_result['user_motion_array_state']['daily_allowed_number']
                expiry_date = user_financial_state_result['user_motion_array_state']['expiry_date']
                message += f'🔵 بسته موشن ارای: موجودی کل {total_tokens} - سقف استفاده روزانه {daily_allowed_number} - مانده کل {total_remaining_tokens} - مانده روزانه {daily_remaining_tokens} - انقضا در {expiry_date}'
                message += '\n'
            message += '\n'

            message += f'🟩 اعتبار مورد نیاز:'
            message += '\n'
            if process_links_results['en_token']:
                if en_link_unhandled == 0:
                    message += f'{en_link_number} برای انواتو (استفاده {en_link_handled} عدد از بسته فعلی)'
                    message += '\n'
                else:
                    message += f'{en_link_number} برای انواتو (استفاده {en_link_handled} عدد از بسته فعلی و استفاده {en_link_unhandled} عدد از اعتبار حساب (ضریب: {en_f}))'
                    message += '\n'
            else:
                if en_link_unhandled > 0:
                    message += f'{en_link_number} برای انواتو (ضریب: {en_f})'
                    message += '\n'
            if process_links_results['ma_token']:
                if ma_link_unhandled == 0:
                    message += f'{ma_link_number} برای موشن ارای (استفاده {ma_link_handled} عدد از بسته فعلی)'
                    message += '\n'
                else:
                    message += f'{ma_link_number} برای موشن ارای (استفاده {ma_link_handled} عدد از بسته فعلی و استفاده {ma_link_unhandled} عدد از اعتبار حساب (ضریب: {ma_f}))'
                    message += '\n'
            else:
                if ma_link_unhandled > 0:
                    message += f'{ma_link_unhandled} برای موشن ارای (ضریب: {ma_f})'
                    message += '\n'
            if process_links_results['user_credit_is_sufficient']['is_sufficient']:
                message += f'مجموع اعتبار مورد نیاز: {total_credit_needed}'
                message += '\n'

                message += '\n'
                message += f'❓ ادامه دهد؟'
                message += '\n'
            else:
                message += '\n'
                message += f'شما دارای بسته فعال نبوده یا اعتبار حساب کافی نیست. لطفا حساب خود را شارژ کنید یا بسته تهیه کنید.'
                message += '\n'
        else:
            message += f'🟦 موجودی اعتبار حساب: {w_cr}'
            message += '\n\n'
            if process_links_results['user_credit_is_sufficient']['is_sufficient']:
                message += f'🟩 اعتبار مورد نیاز:'
                message += '\n'
                message += f'{en_link_number} برای انواتو (ضریب: {en_f})'
                message += '\n'
                message += f'{ma_link_number} برای موشن ارای (ضریب: {ma_f})'
                message += '\n'
                message += f'مجموع اعتبار مورد نیاز: {total_credit_needed}'
                message += '\n'

                message += '\n'
                message += f'❓ ادامه دهد؟'
                message += '\n'
            else:
                message += f'🟩 اعتبار مورد نیاز:'
                message += '\n'
                message += f'{en_link_number} برای انواتو (ضریب: {en_f})'
                message += '\n'
                message += f'{ma_link_number} برای موشن ارای (ضریب: {ma_f})'
                message += '\n'
                message += f'مجموع اعتبار مورد نیاز: {total_credit_needed}'
                message += '\n'

                message += '\n'
                message += f'شما دارای بسته فعال نبوده یا اعتبار حساب کافی نیست. لطفا حساب خود را شارژ کنید یا بسته تهیه کنید.'
                message += '\n'
    else:
        user_financial_state_result = user_financial_state(user)
        if process_links_results['en_token']:
            total_remaining_tokens = user_financial_state_result['user_envato_state']['total_remaining_tokens']
            daily_remaining_tokens = user_financial_state_result['user_envato_state']['daily_remaining_tokens']
            total_tokens = user_financial_state_result['user_envato_state']['total_tokens']
            daily_allowed_number = user_financial_state_result['user_envato_state']['daily_allowed_number']
            expiry_date = user_financial_state_result['user_envato_state']['expiry_date']
            message += f'🔵 بسته انواتو: موجودی کل {total_tokens} - سقف استفاده روزانه {daily_allowed_number} - مانده کل {total_remaining_tokens} - مانده روزانه {daily_remaining_tokens} - انقضا در {expiry_date}'
            message += '\n'
        if process_links_results['ma_token']:
            total_remaining_tokens = user_financial_state_result['user_motion_array_state'][
                'total_remaining_tokens']
            daily_remaining_tokens = user_financial_state_result['user_motion_array_state'][
                'daily_remaining_tokens']
            total_tokens = user_financial_state_result['user_motion_array_state']['total_tokens']
            daily_allowed_number = user_financial_state_result['user_motion_array_state']['daily_allowed_number']
            expiry_date = user_financial_state_result['user_motion_array_state']['expiry_date']
            message += f'🔵 بسته موشن ارای: موجودی کل {total_tokens} - سقف استفاده روزانه {daily_allowed_number} - مانده کل {total_remaining_tokens} - مانده روزانه {daily_remaining_tokens} - انقضا در {expiry_date}'
            message += '\n'
        message += '\n'

        message += f'🟩 اعتبار مورد نیاز:'
        message += '\n'
        if process_links_results['en_token']:
            message += f'{en_link_number} برای انواتو (استفاده {en_link_number} عدد از بسته فعلی)'
            message += '\n'
        if process_links_results['ma_token']:
            message += f'{ma_link_number} برای موشن ارای (استفاده {ma_link_number} عدد از بسته فعلی)'
            message += '\n'
        message += '\n'
        message += f'❓ ادامه دهد؟'
        message += '\n'

    inline_keyboard = [
        [
            {"text": "بله",
             "callback_data": f"process_links_and_apply_charges_{request_detail.id}"},
            {"text": "خیر",
             "callback_data": "🏡 صفحه اصلی"}
        ],
        [
            {"text": "صفحه اصلی",
             "callback_data": "🏡 صفحه اصلی"}
        ]
    ]

    keyboard_markup = {
        "inline_keyboard": inline_keyboard
    }

    process_links_and_send_message_to_telegram_markup = json.dumps(keyboard_markup)

    telegram_http_send_message_via_post_method(chat_id=user.username, text=message,
                                               reply_markup=process_links_and_send_message_to_telegram_markup,
                                               parse_mode='Markdown')


def process_links_and_apply_charge_check(message_text):
    message_text = str(message_text)
    if message_text.find('process_links_and_apply_charges_') != -1:
        return True
    else:
        return False


def process_links_and_apply_charge(user, message_text):
    message_text = str(message_text)
    message_text = message_text.replace('process_links_and_apply_charges_', '')
    request_detail_id = int(message_text)
    request_detail = RequestDetail.objects.get(id=request_detail_id)

    file_page_link_list = json.loads(request_detail.file_page_link_list)
    process_links_results = request_detail.process_links_results

    process_links_results = str(process_links_results)
    process_links_results = process_links_results.split('_')

    en_link_number = int(process_links_results[0])
    en_link_handled = int(process_links_results[1])
    en_link_unhandled = int(process_links_results[2])
    en_links_cost = Decimal(process_links_results[3])

    ma_link_number = int(process_links_results[4])
    ma_link_handled = int(process_links_results[5])
    ma_link_unhandled = int(process_links_results[6])
    ma_links_cost = Decimal(process_links_results[7])

    total_cost = en_links_cost + ma_links_cost
    if total_cost > 0:
        apply_charge_on_credit(user, total_cost)

    if en_link_handled > 0:
        apply_charge_on_token(user, 'envato', en_link_handled)

    if ma_link_handled > 0:
        apply_charge_on_token(user, 'motion_array', ma_link_handled)

    RequestHandler(user=user, file_page_link_list=file_page_link_list, data_track=request_detail_id).start()

    process_links_and_apply_charge_markup = json.dumps(
        {"inline_keyboard": [[{"text": "صفحه اصلی", "callback_data": "🏡 صفحه اصلی"}]]})
    telegram_http_send_message_via_post_method(chat_id=user.username, text='انجام شد',
                                               reply_markup=process_links_and_apply_charge_markup,
                                               parse_mode='Markdown')


def apply_charge_on_credit(user, spend_amount):
    profile = user.user_profile
    profile.wallet_credit -= spend_amount
    profile.save()
    return True


def apply_charge_on_token(user, token_type, token_spend_number):
    user_active_multi_tokens = UserMultiToken.objects.filter(user=user,
                                                             token_type=f'{token_type}',
                                                             disabled=False)
    if user_active_multi_tokens.count() == 0:
        return False
    else:
        user_active_multi_token = user_active_multi_tokens.first()
        user_active_multi_token.total_remaining_tokens -= token_spend_number
        user_active_multi_token.daily_remaining_tokens -= token_spend_number
        user_active_multi_token.save()
        return True


def token_can_handel_number(user, token_type, number_of_links):
    user_active_multi_tokens = UserMultiToken.objects.filter(user=user,
                                                             token_type=f'{token_type}',
                                                             disabled=False)
    if user_active_multi_tokens.count() == 0:
        return 0
    else:
        user_active_multi_token = user_active_multi_tokens.first()
        total_remaining_tokens = user_active_multi_token.total_remaining_tokens
        daily_remaining_tokens = user_active_multi_token.daily_remaining_tokens
        if total_remaining_tokens > daily_remaining_tokens:
            number_of_available_token = daily_remaining_tokens
        else:
            number_of_available_token = total_remaining_tokens

        if number_of_links > number_of_available_token:
            can_handel_number = number_of_available_token
        else:
            can_handel_number = number_of_links
    return can_handel_number


def user_financial_state(user):
    wallet_credit = user.user_profile.wallet_credit
    user_envato_active_multi_tokens = UserMultiToken.objects.filter(user=user,
                                                                    token_type=f'envato',
                                                                    disabled=False)
    user_motion_array_active_multi_tokens = UserMultiToken.objects.filter(user=user,
                                                                          token_type=f'motion_array',
                                                                          disabled=False)
    if user_envato_active_multi_tokens.count() == 0:
        user_envato_state_result = {
            'has_active_token': False,
            'total_remaining_tokens': None,
            'daily_remaining_tokens': None,
            'total_tokens': None,
            'daily_allowed_number': None,
            'expiry_date': None,
            'expiry_days': None,
        }
    else:
        user_envato_active_multi_token = user_envato_active_multi_tokens.first()
        total_remaining_tokens = user_envato_active_multi_token.total_remaining_tokens
        daily_remaining_tokens = user_envato_active_multi_token.daily_remaining_tokens
        total_tokens = user_envato_active_multi_token.total_tokens
        daily_allowed_number = user_envato_active_multi_token.daily_allowed_number
        expiry_date = user_envato_active_multi_token.expiry_date
        expiry_days = user_envato_active_multi_token.expiry_days
        user_envato_state_result = {
            'has_active_token': True,
            'total_remaining_tokens': total_remaining_tokens,
            'daily_remaining_tokens': daily_remaining_tokens,
            'total_tokens': total_tokens,
            'daily_allowed_number': daily_allowed_number,
            'expiry_date': expiry_date.strftime('%Y-%m-%d'),
            'expiry_days': expiry_days,
        }
    if user_motion_array_active_multi_tokens.count() == 0:
        user_motion_array_state_result = {
            'has_active_token': False,
            'total_remaining_tokens': None,
            'daily_remaining_tokens': None,
            'total_tokens': None,
            'daily_allowed_number': None,
            'expiry_date': None,
            'expiry_days': None,
        }
    else:
        user_motion_array_active_multi_token = user_motion_array_active_multi_tokens.first()
        total_remaining_tokens = user_motion_array_active_multi_token.total_remaining_tokens
        daily_remaining_tokens = user_motion_array_active_multi_token.daily_remaining_tokens
        total_tokens = user_motion_array_active_multi_token.total_tokens
        daily_allowed_number = user_motion_array_active_multi_token.daily_allowed_number
        expiry_date = user_motion_array_active_multi_token.expiry_date
        expiry_days = user_motion_array_active_multi_token.expiry_days
        user_motion_array_state_result = {
            'has_active_token': True,
            'total_remaining_tokens': total_remaining_tokens,
            'daily_remaining_tokens': daily_remaining_tokens,
            'total_tokens': total_tokens,
            'daily_allowed_number': daily_allowed_number,
            'expiry_date': expiry_date.strftime('%Y-%m-%d %H:%M'),
            'expiry_days': expiry_days,
        }
    user_financial_state_result = {
        'wallet_credit': wallet_credit,
        'user_envato_state': user_envato_state_result,
        'user_motion_array_state': user_motion_array_state_result,
    }
    return user_financial_state_result


def user_credit_is_sufficient(user, number_of_en_links, number_of_ma_links):
    core_settings = get_core_settings()
    en_cost_factor = core_settings.envato_cost_factor
    ma_cost_factor = core_settings.motion_array_cost_factor

    en_links_costs = number_of_en_links * en_cost_factor
    ma_links_costs = number_of_ma_links * ma_cost_factor
    total_cost = en_links_costs + ma_links_costs

    wallet_credit = user.user_profile.wallet_credit

    if wallet_credit >= total_cost:
        is_sufficient = True
        insufficient_amount = 0
    else:
        is_sufficient = False
        insufficient_amount = total_cost - wallet_credit

    user_credit_is_sufficient_result = {
        'en_cost_factor': en_cost_factor,
        'ma_cost_factor': ma_cost_factor,
        'en_links_costs': en_links_costs,
        'ma_links_costs': ma_links_costs,
        'total_cost': total_cost,
        'wallet_credit': wallet_credit,
        'is_sufficient': is_sufficient,
        'insufficient_amount': insufficient_amount,
    }

    return user_credit_is_sufficient_result
