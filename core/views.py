import json
import threading
import time
import re
import jdatetime
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.views import View
from accounts.models import UserRequestHistory, UserRequestHistoryDetail, UserScraperTokenRedeemHistory, UserMultiToken, \
    user_wallet_charge, create_user_multi_token
from core.models import get_core_settings, File, AriaCode
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


class RequestHandler(threading.Thread):
    def __init__(self, user, file_page_link_list, data_track):
        super().__init__()
        self.user = user
        self.file_page_link_list = file_page_link_list
        self.data_track = data_track

    def run(self):
        try:
            new_user_request_history = UserRequestHistory.objects.create(user=self.user,
                                                                         data_track=json.dumps(self.data_track))
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
                    if file_type == 'MotionArray':
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
        if custom_log_print:
            custom_log('secret_key: ' + str(secret_key))
        if secret_key is not None and str(secret_key) == '12587KFlk54NCJDmvn8541':
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
                    if custom_log_print:
                        custom_log(str(response_list))
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
                custom_log('wrong secret key')
            return False
    except:
        if custom_log_print:
            custom_log('unauthorized access')
        return False


def under_construction_check(user_unique_id, custom_log_print: bool):
    # check if core settings under construction is active
    if get_core_settings().under_construction:
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

    message_text = "ثبت نام شما با موقفیت انجام شد. \n به ربات تلگرام مکسیمم شاپ خوش آمدید. در این ربات می توانید فایل های دلخواه خود را از برترین سایت های دنیا به سادگی چند کلیک دانلود نمایید."
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


def telegram_message_account_state(user_unique_id, user):
    text = f''''''
    profile = user.user_profile
    if profile.multi_token:
        if profile.multi_token.expiry_date > jdatetime.datetime.now():
            text += f'🌌بسته دانلود روزانه({profile.multi_token.daily_count} عدد در روز):'
            text += f'\n'
            text += f'<b>⌛تاریخ انقضا بسته: {profile.multi_token.expiry_date.strftime("%Y/%m/%d %H:%M")}</b>'
            text += f'\n'
            text += f'<b>تعداد مصرف شده در 24 ساعت: {profile.multi_token_daily_used} از {profile.multi_token.daily_count}</b>'
            text += f'\n'
            text += f'(محدودیت دانلود هر 24 ساعت ریست می شود)'
            text += f'\n\n'
    text += f'⭐بسته اعتباری: {profile.single_tokens.filter(is_used=False, expiry_date__gte=jdatetime.datetime.now()).count()} عدد (تاریخ انقضا: ⌛ نامحدود)'
    text += f'\n\n'
    telegram_http_send_message_via_post_method(chat_id=user_unique_id, text=text,
                                               parse_mode='HTML')


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


def telegram_message_fetch_data_accept_1(user_unique_id, user):
    profile = user.user_profile
    if profile.user_latest_requested_files == 'expired':
        telegram_http_send_message_via_get_method(chat_id=user_unique_id,
                                                  text=f'درخواست معتبر نمی باشد')
        return JsonResponse({'message': 'a requests has been handled'})
    file_page_link_list = json.loads(profile.user_latest_requested_files)
    profile.user_latest_requested_files = 'expired'
    user_all_requests_history = UserRequestHistory.objects.filter(user=user)
    similar_request_list = []
    user_request_history_files_unique = []
    for user_request_history in user_all_requests_history:
        user_request_history_all_files = user_request_history.files.all()
        for user_request_history_file in user_request_history_all_files:
            user_request_history_files_unique.append(user_request_history_file)
    user_request_history_files_unique = list(set(user_request_history_files_unique))
    for user_request_history_file_unique in user_request_history_files_unique:
        for file_page_link in file_page_link_list:
            if user_request_history_file_unique.unique_code == file_page_link[2]:
                similar_request_list.append(file_page_link[2])

    custom_log(f'file_page_link_list: {len(file_page_link_list)}')
    custom_log(f'similar_request_list: {len(similar_request_list)}')
    profile.daily_used_total += (len(file_page_link_list) - len(similar_request_list))
    profile.multi_token_daily_used += (len(file_page_link_list) - len(similar_request_list))
    profile.save()
    data_track = {
        'just_daily': 'true',
        'daily_and_single': 'false',
        'daily_used_number': (len(file_page_link_list) - len(similar_request_list)),
        'single_used_tokens_id': 'zero',
        'just_single': 'false',
    }
    RequestHandler(user=user, file_page_link_list=file_page_link_list, data_track=data_track).start()
    if len(similar_request_list) > 0:
        telegram_http_send_message_via_get_method(chat_id=user_unique_id,
                                                  text=f'مقدار وارد شده تایید و برای شما محاسبه شد.({len(similar_request_list)} فایل تکراری می باشند و محاسبه نخواهند شد) سقف مجاز دانلود تا انتهای امروز {abs(profile.daily_limit - profile.daily_used_total)} عدد می باشد. لیمیت روزانه هر 24 ساعت ریست خواهد شد. ')
    else:
        telegram_http_send_message_via_get_method(chat_id=user_unique_id,
                                                  text=f'مقدار وارد شده تایید و برای شما محاسبه شد. سقف مجاز دانلود تا انتهای امروز {abs(profile.daily_limit - profile.daily_used_total)} عدد می باشد. لیمیت روزانه هر 24 ساعت ریست خواهد شد. ')


def telegram_message_fetch_data_accept_2(user_unique_id, user):
    today = jdatetime.datetime.now()
    profile = user.user_profile
    if profile.user_latest_requested_files == 'expired':
        telegram_http_send_message_via_get_method(chat_id=user_unique_id,
                                                  text=f'درخواست معتبر نمی باشد')
        return JsonResponse({'message': 'a requests has been handled'})
    file_page_link_list = json.loads(profile.user_latest_requested_files)
    profile.user_latest_requested_files = 'expired'
    user_all_requests_history = UserRequestHistory.objects.filter(user=user)
    similar_request_list = []
    user_request_history_files_unique = []
    for user_request_history in user_all_requests_history:
        user_request_history_all_files = user_request_history.files.all()
        for user_request_history_file in user_request_history_all_files:
            user_request_history_files_unique.append(user_request_history_file)
    user_request_history_files_unique = list(set(user_request_history_files_unique))
    for user_request_history_file_unique in user_request_history_files_unique:
        for file_page_link in file_page_link_list:
            if user_request_history_file_unique.unique_code == file_page_link[2]:
                similar_request_list.append(file_page_link[2])
    x1 = abs(profile.multi_token.daily_count - profile.multi_token_daily_used)
    x2 = abs((len(file_page_link_list) - len(similar_request_list)) - x1)

    profile.daily_used_total += (len(file_page_link_list) - len(similar_request_list))
    profile.multi_token_daily_used = profile.multi_token.daily_count
    profile.save()

    user_tokens = profile.single_tokens.filter(is_used=False, expiry_date__gte=today)
    used_token_list = []
    for i in range(0, x2):
        for user_token in user_tokens:
            user_token.is_used = True
            user_token.save()
            used_token_list.append(user_token.id)
            break
    data_track = {
        'just_daily': 'false',
        'daily_and_single': 'true',
        'daily_used_number': x1,
        'single_used_tokens_id': used_token_list,
        'just_single': 'false',
    }
    RequestHandler(user=user, file_page_link_list=file_page_link_list, data_track=data_track).start()
    if len(similar_request_list) > 0:
        telegram_http_send_message_via_get_method(chat_id=user_unique_id,
                                                  text=f'مقدار وارد شده تایید و برای شما محاسبه شد.(تعداد {len(similar_request_list)} فایل تکراری است و محاسبه نخواهد شد) سقف مجاز دانلود تا انتهای امروز {abs(profile.daily_limit - profile.daily_used_total)} عدد می باشد. لیمیت روزانه هر 24 ساعت ریست خواهد شد. ')
    else:
        telegram_http_send_message_via_get_method(chat_id=user_unique_id,
                                                  text=f'مقدار وارد شده تایید و برای شما محاسبه شد. سقف مجاز دانلود تا انتهای امروز {abs(profile.daily_limit - profile.daily_used_total)} عدد می باشد. لیمیت روزانه هر 24 ساعت ریست خواهد شد. ')


def telegram_message_fetch_data_accept_3(user_unique_id, user):
    today = jdatetime.datetime.now()
    profile = user.user_profile
    if profile.user_latest_requested_files == 'expired':
        telegram_http_send_message_via_get_method(chat_id=user_unique_id,
                                                  text=f'درخواست معتبر نمی باشد')
        return JsonResponse({'message': 'a requests has been handled'})
    file_page_link_list = json.loads(profile.user_latest_requested_files)
    profile.user_latest_requested_files = 'expired'
    user_all_requests_history = UserRequestHistory.objects.filter(user=user)
    similar_request_list = []
    user_request_history_files_unique = []
    for user_request_history in user_all_requests_history:
        user_request_history_all_files = user_request_history.files.all()
        for user_request_history_file in user_request_history_all_files:
            user_request_history_files_unique.append(user_request_history_file)
    user_request_history_files_unique = list(set(user_request_history_files_unique))
    for user_request_history_file_unique in user_request_history_files_unique:
        for file_page_link in file_page_link_list:
            if user_request_history_file_unique.unique_code == file_page_link[2]:
                similar_request_list.append(file_page_link[2])
    profile.daily_used_total += (len(file_page_link_list) - len(similar_request_list))
    profile.save()

    user_tokens = profile.single_tokens.filter(is_used=False, expiry_date__gte=today)
    user_tokens_query_list = []
    for user_token_obj in user_tokens:
        user_tokens_query_list.append(user_token_obj)
    used_token_list = []
    i = 0
    for number in range(0, (len(file_page_link_list) - len(similar_request_list))):
        for user_token in user_tokens_query_list:
            user_token.is_used = True
            user_token.save()
            used_token_list.append(user_token.id)
            user_tokens_query_list = user_tokens_query_list[1:]
            break
        i += 1
        custom_log(str(i))
    custom_log(used_token_list)    
    data_track = {
        'just_daily': 'false',
        'daily_and_single': 'false',
        'daily_used_number': 'zero',
        'single_used_tokens_id': used_token_list,
        'just_single': 'true',
    }
    RequestHandler(user=user, file_page_link_list=file_page_link_list, data_track=data_track).start()
    if len(similar_request_list) > 0:
        telegram_http_send_message_via_get_method(chat_id=user_unique_id,
                                                  text=f'مقدار وارد شده تایید و برای شما محاسبه شد.(تعداد {len(similar_request_list)} فایل تکراری است و محاسبه نخواهد شد) سقف مجاز دانلود تا انتهای امروز {abs(profile.daily_limit - profile.daily_used_total)} عدد می باشد. لیمیت روزانه هر 24 ساعت ریست خواهد شد. ')
    else:
        telegram_http_send_message_via_get_method(chat_id=user_unique_id,
                                                  text=f'مقدار وارد شده تایید و برای شما محاسبه شد. سقف مجاز دانلود تا انتهای امروز {abs(profile.daily_limit - profile.daily_used_total)} عدد می باشد. لیمیت روزانه هر 24 ساعت ریست خواهد شد. ')
    return JsonResponse({'message': 'a requests has been handled'})


def redeem_new_token_check(message_text):
    message_text = str(message_text)
    message_text = message_text.replace('Envato-', '')
    message_text = message_text.replace('Motion-', '')
    if len(str(message_text)) == 19 and str(message_text)[4] == '-' and str(message_text)[9] == '-' and \
            str(message_text)[14] == '-':
        return True
    else:
        return False


def redeem_new_token_callback_check(message_text):
    message_text = str(message_text)
    if message_text.find('redeem_callback_yes_') != -1:
        return True
    else:
        return False


def redeem_new_token(token_unique_code, user, user_unique_id):
    token_unique_code = str(token_unique_code)
    if token_unique_code.find('Envato') != -1:
        token_state = create_user_multi_token(user, 'envato', token_unique_code)
        handle_token_state('envato', token_state, token_unique_code)
    elif token_unique_code.find('Motion') != -1:
        token_state = create_user_multi_token(user, 'motion_array', token_unique_code)
        handle_token_state('motion_array', token_state, token_unique_code)
    else:
        user_wallet_charge(user, token_unique_code)

    return JsonResponse({'message': f'redeem_new_token: {user_unique_id}'})


def handle_token_state(token_type, token_state, new_token_unique_code):
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

    support_reply_markup = json.dumps(keyboard_markup)

    if token_state[0] == 'old_active_exist':
        message = f'"بسته اشتراک ماهانه انواتو - {token_state[1].total_tokens} دانلود – {token_state[1].expiry_days} روزه" با سقف دانلود " دانلود – {token_state[1].daily_allowed_number} عدد در روز " تا تاریخ ایکس فعال است.'
        message += '\n'
        message += 'امکان ثبت بسته جدید از این نوع ندارید. در صورت مواجه شدن با محدودیت دانلود روزانه در"بسته های اشتراک ماهانه" می توانید با خرید "بسته های اعتباری نامحدود زمانی" دانلود های خود را انجام دهید.'
        message += '\n'
        message += 'همچنین لایسنس وارد شده را بعد از اتمام بسته فعلی خود می توانید استفاده کنید.'
        telegram_http_send_message_via_post_method(chat_id=token_state[1].user.username, text=message,
                                                   reply_markup=support_reply_markup, parse_mode='Markdown')
    elif token_state[0] == 'new_one_is_used_before':
        message = f'توکن وارد شده با مقدار {token_state[1]} قبلا استفاده شده است'
        telegram_http_send_message_via_post_method(chat_id=token_state[1].user.username, text=message,
                                                   reply_markup=support_reply_markup, parse_mode='Markdown')
    elif token_state[0] == 'new_one_is_created':
        message = f'شما در حال فعال سازی "بسته اشتراک ماهانه انواتو – ایکس دانلود – ایکس روزه " با سقف دانلود " ایکس عدد  در روز" می باشید.'
        message += '\n'
        message += 'تاریخ انقضا این بسته بعد از فعال سازی ایکس روز خواهد بود.'
        message += '\n'
        message += 'در صورت داشتن اعتبار و همچنین بسته اشتراکی، اولویت با بسته اشتراکی خواهد بود و از اعتبارحساب شما کاسته نخواهد شد.'
        message += '\n'
        message += 'فعال شود؟'
    elif token_state[0] == 'new_one_is_not_found_in_db':
        message = f'توکن وارد شده با مقدار {token_state[1]} یافت نشد'
        telegram_http_send_message_via_post_method(chat_id=token_state[1].user.username, text=message,
                                                   reply_markup=support_reply_markup, parse_mode='Markdown')
    else:
        message = f'توکن وارد شده با مقدار {token_state[1]} بدون ثبت وضعیت مشخص'
        telegram_http_send_message_via_post_method(chat_id=token_state[1].user.username, text=message,
                                                   reply_markup=support_reply_markup, parse_mode='Markdown')


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


def user_quote_limit_check(message_text, user_unique_id, user, custom_log_print: bool):
    profile = user.user_profile
    if profile.daily_used_total >= profile.daily_limit:
        if custom_log_print:
            custom_log(f'تعداد درخواست های مجاز روزانه {user_unique_id} به حد اکثر رسیده است')
        text = 'تعداد درخواست های مجاز روزانه شما به حد اکثر رسیده است'
        telegram_http_send_message_via_post_method(chat_id=user_unique_id, text=text, parse_mode='HTML')
        return False
    else:
        return True


def user_has_active_plan_check(user_unique_id, user, custom_log_print: bool):
    today = jdatetime.datetime.now()
    profile = user.user_profile
    user_multi_token = profile.multi_token
    if user_multi_token:
        if not user_multi_token.expiry_date > today:
            user_multi_token = None
    user_single_tokens = profile.single_tokens.filter(is_used=False, expiry_date__gte=today)

    if user_multi_token is None and user_single_tokens.count() == 0:
        message = f'بسته فعالی ندارید. جهت تهیه بسته به لینک زیر مراجعه نمایید'
        message += '\n\n'
        message += 'https://maxish.ir'
        if custom_log_print:
            custom_log(f'کاربر {user_unique_id} بسته فعالی ندارد.')
        telegram_http_send_message_via_post_method(chat_id=user_unique_id, text=message, parse_mode='HTML')
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
            file_page_link_list.append(['MotionArray', file_page_link, unique_code])
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


def file_link_list_handler(user_unique_id, user, file_page_link_list):
    profile = user.user_profile
    user_multi_token = profile.multi_token
    user_single_tokens = profile.single_tokens.all()
    if len(file_page_link_list) + profile.daily_used_total > profile.daily_limit:
        sd = abs((len(file_page_link_list) + profile.daily_used_total) - profile.daily_limit)
        telegram_http_send_message_via_get_method(chat_id=user_unique_id,
                                                  text=f'موارد درخواستی به تعداد {sd} عدد بزرگتر از سقف تعداد درخواست روزانه شما می باشد')
        return JsonResponse({'message': 'a requests has been handled'})

    custom_log('RequestFile-> مقدار ورودی توسط پردازشگر ربات در حال بررسی می باشد')
    telegram_http_send_message_via_get_method(chat_id=user_unique_id,
                                              text='مقدار ورودی توسط پردازشگر ربات در حال بررسی می باشد')
    time.sleep(1)

    if user_multi_token is not None:
        if profile.multi_token_daily_used < user_multi_token.daily_count:
            sd = (user_multi_token.daily_count - profile.multi_token_daily_used) - len(
                file_page_link_list)
            if sd >= 0:
                inline_keyboard = [
                    [
                        {"text": "بله",
                         "callback_data": "fetch_data_accept_1"},
                        {"text": "خیر",
                         "callback_data": "دانلود فایل"}
                    ],
                    [
                        {"text": "صفحه اصلی",
                         "callback_data": "دانلود فایل"}
                    ]
                ]

                keyboard_markup = {
                    "inline_keyboard": inline_keyboard
                }

                support_reply_markup = json.dumps(keyboard_markup)

                support_message_text = f"ایا جهت دریافت فایل های زیر به تعداد {len(file_page_link_list)} عدد مطمئن هستید؟"
                support_message_text += '\n\n'
                i = 1
                for file_page_link in file_page_link_list:
                    support_message_text += f'{i}- کد: {file_page_link[2]}'
                    support_message_text += '\n'
                    i += 1
                telegram_http_send_message_via_post_method(chat_id=user_unique_id,
                                                           text=support_message_text,
                                                           reply_markup=support_reply_markup,
                                                           parse_mode='Markdown')
                profile.user_latest_requested_files = json.dumps(file_page_link_list)
                profile.save()
                return JsonResponse({'message': 'a requests decision has been made'})
            else:
                if abs(sd) <= user_single_tokens.count():
                    custom_log(abs(sd))
                    custom_log(user_single_tokens.count())
                    inline_keyboard = [
                        [
                            {"text": "تایید",
                             "callback_data": "fetch_data_accept_2"},
                            {"text": "انصراف",
                             "callback_data": "دانلود فایل"}
                        ],
                        [
                            {"text": "صفحه اصلی",
                             "callback_data": "دانلود فایل"}
                        ]
                    ]

                    keyboard_markup = {
                        "inline_keyboard": inline_keyboard
                    }

                    support_reply_markup = json.dumps(keyboard_markup)
                    support_message_text = f'موارد درخواستی به تعداد {abs(sd)} عدد بزرگتر از بسته روزانه شما می باشد. در صورت ادامه از توکن های تکی شما کسر خواهد شد. '
                    support_message_text += '\n\n'
                    support_message_text += f"ایا جهت دریافت فایل های زیر به تعداد {len(file_page_link_list)} عدد مطمئن هستید؟"
                    support_message_text += '\n\n'
                    i = 1
                    for file_page_link in file_page_link_list:
                        support_message_text += f'{i}- کد: {file_page_link[2]}'
                        support_message_text += '\n'
                        i += 1
                    telegram_http_send_message_via_post_method(chat_id=user_unique_id,
                                                               text=support_message_text,
                                                               reply_markup=support_reply_markup,
                                                               parse_mode='Markdown')
                    profile.user_latest_requested_files = json.dumps(file_page_link_list)
                    profile.save()
                    return JsonResponse({'message': 'a requests decision has been made'})
                else:
                    message = f'موارد درخواستی به تعداد {abs(sd)} عدد بزرگتر از سقف دانلود بسته روزانه شما می باشد. در صورت نیاز به دانلود بیشتر می توانید از لینک زیر توکن تهیه نمایید. سقف مجاز دانلود تا انتهای امروز {abs(profile.daily_limit - profile.daily_used_total)} می باشد. '
                    message += '\n\n'
                    message += 'https://maxish.ir'
                    telegram_http_send_message_via_get_method(chat_id=user_unique_id,
                                                              text=message)
                    return JsonResponse({'message': 'a requests has been handled'})
        else:
            if user_single_tokens.count() == 0:
                message = f'سقف دانلود بسته روزانه شما به حداکثر رسیده و توکن فعالی ندارید. سقف مجاز دانلود تا انتهای امروز {abs(profile.daily_limit - profile.daily_used_total)} عدد می باشد. جهت تهیه بسته بر روی لینک زیر کلیک کنید'
                message += '\n\n'
                message += 'https://maxish.ir'
                telegram_http_send_message_via_get_method(chat_id=user_unique_id,
                                                          text=message)
                return JsonResponse({'message': 'a requests has been handled'})
    else:
        from_daily_token_message = 'توکن روزانه ندارید'
    if user_single_tokens.count() != 0:
        if user_single_tokens.count() == 0:
            message = f'توکن فعالی ندارید. سقف مجاز دانلود تا انتهای امروز {abs(profile.daily_limit - profile.daily_used_total)} عدد می باشد. جهت تهیه بسته بر روی لینک زیر کلیک کنید'
            message += '\n\n'
            message += 'https://maxish.ir'
            telegram_http_send_message_via_get_method(chat_id=user_unique_id,
                                                      text=message)
            return JsonResponse({'message': 'a requests has been handled'})

        elif len(file_page_link_list) <= user_single_tokens.count():
            inline_keyboard = [
                [
                    {"text": "تایید",
                     "callback_data": "fetch_data_accept_3"},
                    {"text": "انصراف",
                     "callback_data": "دانلود فایل"}
                ],
                [
                    {"text": "صفحه اصلی",
                     "callback_data": "دانلود فایل"}
                ]
            ]

            keyboard_markup = {
                "inline_keyboard": inline_keyboard
            }

            support_reply_markup = json.dumps(keyboard_markup)
            support_message_text = f"ایا جهت دریافت فایل های زیر به تعداد {len(file_page_link_list)} عدد مطمئن هستید؟"
            support_message_text += '\n\n'
            i = 1
            for file_page_link in file_page_link_list:
                support_message_text += f'{i}- کد: {file_page_link[2]}'
                support_message_text += '\n'
                i += 1
            telegram_http_send_message_via_post_method(chat_id=user_unique_id,
                                                       text=support_message_text,
                                                       reply_markup=support_reply_markup,
                                                       parse_mode='Markdown')
            profile.user_latest_requested_files = json.dumps(file_page_link_list)
            profile.save()
            return JsonResponse({'message': 'a requests decision has been made'})

        else:
            sd = abs(len(file_page_link_list) - user_single_tokens.count())
            message = f'موارد درخواستی به تعداد {sd} عدد بزرگتر از تعداد توکن های فعال شما می باشد. جهت تهیه توکن بر روی دکمه زیر کلیک نمایید'
            message += '\n\n'
            message += 'https://maxish.ir'
            telegram_http_send_message_via_get_method(chat_id=user_unique_id,
                                                      text=message)
            return JsonResponse({'message': 'a requests has been handled'})