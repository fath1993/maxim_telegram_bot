import json
import threading
import time
import re
import jdatetime
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.views import View
from accounts.models import UserRequestHistory, UserRedeemHistory, RedeemDownloadToken, UserRequestHistoryDetail, \
    SingleToken, MultiToken
from core.models import get_core_settings, File
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
            secret_key = request.META['HTTP_X_TELEGRAM_BOT_API_SECRET_TOKEN']
            custom_log('secret_key: ' + str(secret_key))
        except:
            secret_key = None
            custom_log('unauthorized access')
        if secret_key is not None and str(secret_key) == '12587KFlk54NCJDmvn8541':
            front_input = json.loads(request.body)
            custom_log(str(front_input))
            try:
                try:
                    user_unique_id = front_input['callback_query']['from']['id']
                    user_first_name = front_input['callback_query']['from']['first_name']
                    message_text = front_input['callback_query']['data']
                    message_text_check = str(message_text).split(',')
                    if message_text_check[0] == 'payment':
                        message_text = 'payment'
                        vip_plan_type = message_text_check[1]
                        vip_plan_id = message_text_check[2]
                except:
                    user_unique_id = front_input['message']['from']['id']
                    user_first_name = front_input['message']['from']['first_name']
                    message_text = str(front_input['message']['text'])
                custom_log(str(user_unique_id))
                custom_log(str(user_first_name))
                custom_log(str(message_text))
                try:
                    user = User.objects.get(username=user_unique_id)
                except:
                    user = User.objects.create_user(username=user_unique_id, first_name=user_first_name)
                if message_text == '/start' or message_text == "🔙 بازگشت" or message_text == "🏡 صفحه اصلی" or message_text == 'payment_term_agree_no':
                    # Define the menu buttons
                    menu_buttons = [
                        ["راهنمای دانلود", "دانلود فایل"],
                        ["ورود به سایت"],
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

                    # Send a message with the menu buttons
                    message_text = "به ربات تلگرام مکسیش شاپ خوش آمدید در این ربات می توانید فایل های دلخواه خود را از برترین سایت های دنیا به سادگی چند کلیک دانلود نمایید"

                    telegram_http_send_message_via_post_method(chat_id=user_unique_id, text=message_text,
                                                               reply_markup=reply_markup, parse_mode='Markdown')
                elif message_text == 'راهنمای دانلود':
                    message_text = f'''
                                    لطفاً جهت دانلود از سایت <a href="https://www.uplooder.net/img/image/61/88597ff6b31d3f78134a9ce2c5dc67b2/help1.png">Envato Elements</a> همانند تصویر زیر لینک فایل مورد نظر را کپی کرده و در ربات وارد کنید. \n لینک های مورد نظر را میتوانید بصورت تک به تک و یا در یک پیام (هر لینک در یک خط) ارسال کنید. \n توجه داشته باشید که پس از ارسال لینک ربات بصورت خودکار شروع به دانلود فایل مورد نظر خواهد کرد. به همین جهت در صورت ارسال لینک و یا کد اشتباه مبلغ حساب شما عودت داده نمی شود.
                                    '''
                    telegram_http_send_message_via_post_method(chat_id=user_unique_id, text=message_text,
                                                               parse_mode='HTML')
                elif message_text == 'دانلود فایل':
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
                elif message_text == 'دانلود از Envato Elements':
                    message_text = f'''
                                    لطفاً جهت دانلود از سایت <a href="https://www.uplooder.net/img/image/61/88597ff6b31d3f78134a9ce2c5dc67b2/help1.png">Envato Elements</a> همانند تصویر زیر لینک فایل مورد نظر را کپی کرده و در ربات وارد کنید. \n لینک های مورد نظر را میتوانید بصورت تک به تک و یا در یک پیام (هر لینک در یک خط) ارسال کنید. \n توجه داشته باشید که پس از ارسال لینک ربات بصورت خودکار شروع به دانلود فایل مورد نظر خواهد کرد. به همین جهت در صورت ارسال لینک و یا کد اشتباه مبلغ حساب شما عودت داده نمی شود.
                                    '''
                    telegram_http_send_message_via_post_method(chat_id=user_unique_id, text=message_text,
                                                               parse_mode='HTML')
                elif message_text == 'ورود به سایت':
                    text = f'''
                    <a href="https://maxish.ir/">جهت مشاهده سایت و محصولات دیگر گروه مکسیموم شاپ کلیک کنید</a> 
                    '''
                    telegram_http_send_message_via_post_method(chat_id=user_unique_id, text=text,
                                                               parse_mode='HTML')
                elif message_text == 'تغییر زبان':
                    text = f'''
                           با عرض پوزش در حال حاضر این مورد غیر فعال میباشد و طی آپدیت های بعدی ربات، منو زبان انگلیسی افزوده خواهد شد. 
                           '''
                    telegram_http_send_message_via_post_method(chat_id=user_unique_id, text=text,
                                                               parse_mode='HTML')
                elif message_text == 'خرید عمده و همکاری':
                    text = f'''
                            ربات مکسیموم شاپ در خصوصی کابران و همکارانی که خرید با تعداد بالا دارد بسته های اختصاصی را قرار داده است که کاربران می توانند با خرید این بسته های مقرون بصرفه شروع با فایل های خود کنند. \n در صورت پشتیبانی مستقیم و ایجاد ارتباط با آیدی زیر در ارتباط باشید. \n <a href="https://t.me/Maximum_S">https://t.me/Maximum_S</a>
                            '''
                    telegram_http_send_message_via_post_method(chat_id=user_unique_id, text=text,
                                                               parse_mode='HTML')
                elif message_text == 'لیست دانلود ها':
                    user_requests_history = UserRequestHistory.objects.filter(user=user)
                    user_download_list = []
                    for user_request_history in user_requests_history:
                        for envato_file in user_request_history.files.all():
                            user_download_list.append(envato_file)
                    user_request_history = list(set(user_download_list))

                    finished_request_successful_list = []
                    for file in user_request_history:
                        if file.download_percentage == 100:
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
                                text += f'⬇️{i}- EnvatoElement_{file.unique_code} - <a href="{BASE_URL}{file.file.url}">لینک دانلود</a>'
                                text += '\n'
                                i += 1
                    telegram_http_send_message_via_post_method(chat_id=user_unique_id, text=text,
                                                               parse_mode='HTML')
                elif message_text == 'گزارش حسابداری':
                    user_redeems_history = UserRedeemHistory.objects.filter(user=user)
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
                                        days=user_redeem_history.redeemed_token.expiry_days)) > self.today:
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
                elif message_text == 'شارژ حساب':
                    message = f'جهت خرید بسته های دانلود به آدرس زیر مراجه نمایید'
                    message += '\n\n'
                    message += 'https://maxish.ir'
                    telegram_http_send_message_via_get_method(chat_id=user_unique_id,
                                                              text=message)
                    return JsonResponse({'message': 'a requests has been handled'})
                elif message_text == 'مشاهده موجودی':
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
                elif message_text == 'بخش پشتیبانی':
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

                    support_message_text = "آیا سوالی دارید؟"
                    telegram_http_send_message_via_post_method(chat_id=user_unique_id, text=support_message_text,
                                                               reply_markup=support_reply_markup, parse_mode='Markdown')
                elif message_text == 'support_callback_yes':
                    message = f'جهت ارتباط با پشتیبانی با ایدی زیر در ارتباط باشید'
                    message += '\n\n'
                    message += 'https://t.me/Maximum_S'
                    telegram_http_send_message_via_get_method(chat_id=user_unique_id,
                                                              text=message)
                    return JsonResponse({'message': 'a requests has been handled'})
                elif message_text == 'support_callback_no':
                    pass
                elif message_text == 'درباره':
                    text = f'''
                            درباره
                            '''
                    telegram_http_send_message_via_post_method(chat_id=user_unique_id, text=text,
                                                               parse_mode='HTML')
                elif message_text == 'راهنما':
                    text = f'''
                            راهنما
                            '''
                    telegram_http_send_message_via_post_method(chat_id=user_unique_id, text=text,
                                                               parse_mode='HTML')
                elif message_text == 'پروفایل کاربری':
                    menu_buttons = [
                        ["خرید عمده و همکاری", 'تغییر زبان', 'شارژ حساب'],
                        ["مشاهده موجودی", 'گزارش حسابداری', 'لیست دانلود ها'],
                        ["راهنما", 'درباره', 'بخش پشتیبانی'],
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
                elif message_text == 'fetch_data_accept_1':
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
                    return JsonResponse({'message': 'a requests has been handled'})

                elif message_text == 'fetch_data_accept_2':
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

                    user_tokens = profile.single_tokens.filter(is_used=False, expiry_date__gte=self.today)
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
                    return JsonResponse({'message': 'a requests has been handled'})

                elif message_text == 'fetch_data_accept_3':
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

                    user_tokens = profile.single_tokens.filter(is_used=False, expiry_date__gte=self.today)
                    used_token_list = []
                    for number in range(0, (len(file_page_link_list) - len(similar_request_list))):
                        for user_token in user_tokens:
                            user_token.is_used = True
                            user_token.save()
                            used_token_list.append(user_token.id)
                            break
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
                                                                  text=f'مقدار وارد شده تایید و برای شما محاسبه شد. سقف مجاز دانلود تا انتهای امروز {abs(profile.daily_limit - profile.daily_used_total)} عدد می باشد. لیمیت روزانه هر 24 ساعت ریست خواهد شد. ')
                    else:
                        telegram_http_send_message_via_get_method(chat_id=user_unique_id,
                                                                  text=f'مقدار وارد شده تایید و برای شما محاسبه شد.(تعداد {len(similar_request_list)} فایل تکراری است و محاسبه نخواهد شد) سقف مجاز دانلود تا انتهای امروز {abs(profile.daily_limit - profile.daily_used_total)} عدد می باشد. لیمیت روزانه هر 24 ساعت ریست خواهد شد. ')
                    return JsonResponse({'message': 'a requests has been handled'})

                else:
                    # check if core settings under construction is active
                    if get_core_settings().under_construction:
                        telegram_http_send_message_via_get_method(chat_id=user_unique_id,
                                                                  text='ربات در حال حاضر قادر به خدمات دهی نمی باشد')
                        time.sleep(1)
                        custom_log('service core setting *under construction* is active')
                        return JsonResponse(
                            {'message': 'under construction'})
                    profile = user.user_profile
                    user_multi_token = user.user_profile.multi_token
                    if user_multi_token:
                        if not user_multi_token.expiry_date > self.today:
                            user_multi_token = None
                    user_single_tokens = user.user_profile.single_tokens.filter(is_used=False,
                                                                                expiry_date__gte=self.today)

                    # check if user try to register new token
                    if len(str(message_text)) == 19 and str(message_text)[4] == '-' and str(message_text)[9] == '-' and str(message_text)[14] == '-':
                        try:
                            redeem_token = RedeemDownloadToken.objects.get(token_unique_code=message_text)
                            if redeem_token.token_type == 'single':
                                for i in range(0, redeem_token.tokens_count):
                                    new_single_token = SingleToken.objects.create(
                                        is_used=False,
                                        expiry_date=jdatetime.datetime.now() + jdatetime.timedelta(
                                            days=redeem_token.expiry_days),
                                    )
                                    profile.single_tokens.add(new_single_token)
                            else:
                                if user_multi_token is not None:
                                    message = f'بسته روزانه با سقف {user_multi_token.daily_count} عدد تا تاریخ {user_multi_token.expiry_date.strftime("%Y/%m/%d %H:%M")} فعال است و امکان ثبت بسته جدید از این نوع ندارید'
                                    message += '\n'
                                    message += 'در صورت مواجه شدن با لیمیت روزانه بسته های نامحدود میتوانید با خرید توکن دانلود های خود را انجام دهید. همچنین کد وارد شده را میتوانید بعد از اتمام بسته نامحدود فعلی وارد کنید'
                                    telegram_http_send_message_via_get_method(chat_id=user_unique_id,
                                                                              text=message)
                                    custom_log(f'{message} :register new redeem-code failed')
                                    return JsonResponse(
                                        {'message': f'{message}'})
                                new_multi_token = MultiToken.objects.create(
                                    is_used=False,
                                    daily_count=redeem_token.tokens_count,
                                    expiry_date=jdatetime.datetime.now() + jdatetime.timedelta(
                                        days=redeem_token.expiry_days),
                                )
                                profile.multi_token = new_multi_token
                            profile.save()
                            redeem_token.is_used = True
                            redeem_token.save()
                            new_user_redeem_history = UserRedeemHistory.objects.create(
                                user=profile.user,
                                redeemed_token=redeem_token,
                            )
                            message = f'کد لایسنس با شناسه {message_text} با موفقیت ثبت شد'
                            if profile.multi_token:
                                if profile.multi_token.expiry_date > jdatetime.datetime.now():
                                    message += f'🌌بسته دانلود روزانه({profile.multi_token.daily_count} عدد در روز):'
                                    message += f'\n'
                                    message += f'<b>⌛تاریخ انقضا بسته: {profile.multi_token.expiry_date.strftime("%Y/%m/%d %H:%M")}</b>'
                                    message += f'\n'
                                    message += f'<b>تعداد مصرف شده در 24 ساعت: {profile.multi_token_daily_used} از {profile.multi_token.daily_count}</b>'
                                    message += f'\n'
                                    message += f'(محدودیت دانلود هر 24 ساعت ریست می شود)'
                                    message += f'\n\n'
                            message += f'⭐بسته اعتباری: {profile.single_tokens.filter(is_used=False, expiry_date__gte=jdatetime.datetime.now()).count()} عدد (تاریخ انقضا: ⌛ نامحدود)'
                            message += f'\n\n'
                            telegram_http_send_message_via_post_method(chat_id=user_unique_id, text=message,
                                                                       parse_mode='HTML')
                            return JsonResponse(
                                {'message': 'ok'})
                        except:
                            message = f'توکن با شناسه {message_text} یافت نشد.'
                            telegram_http_send_message_via_get_method(chat_id=user_unique_id,
                                                                      text=message)
                            custom_log(f'{message} :token not found')
                            return JsonResponse(
                                {'message': f'{message}'})

                    if user_multi_token is None and user_single_tokens.count() == 0:
                        message = f'بسته فعالی ندارید. جهت تهیه بسته به لینک زیر مراجعه نمایید'
                        message += '\n\n'
                        message += 'https://maxish.ir'
                        telegram_http_send_message_via_get_method(chat_id=user_unique_id,
                                                                  text=message)
                        return JsonResponse({'message': 'a requests has been handled'})

                    if profile.updated_at.day != self.today.day:
                        profile.daily_used_total = 0
                        profile.multi_token_daily_used = 0
                        profile.save()
                    if profile.daily_used_total >= profile.daily_limit:
                        telegram_http_send_message_via_get_method(chat_id=user_unique_id,
                                                                  text='تعداد درخواست های مجاز روزانه شما به حد اکثر رسیده است')
                        return JsonResponse({'message': 'a requests has been handled'})

                    # check if received message is acceptable
                    if len(str(message_text)) > 3000:
                        telegram_http_send_message_via_get_method(chat_id=user_unique_id,
                                                                  text='طول پیام ورودی بیشتر از حد مجاز می باشد')
                        custom_log('طول پیام ورودی بیشتر از حد مجاز می باشد :file_page_links')
                        return JsonResponse({'message': 'طول پیام ورودی بیشتر از حد مجاز می باشد :file_page_links'})

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
                        else:
                            pass
                    if len(file_page_link_list) != 0:
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
                                sd = (user_multi_token.daily_count - profile.multi_token_daily_used) - len(file_page_link_list)
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

                    else:
                        custom_log('RequestFile-> مقدار وارد شده صحیح نمی باشد')
                        telegram_http_send_message_via_get_method(chat_id=user_unique_id,
                                                                  text='مقدار وارد شده صحیح نمی باشد')
                        return JsonResponse(
                            {'message': 'RequestFile-> مقدار وارد شده صحیح نمی باشد'})
                return JsonResponse({'message': 'ok'})
            except Exception as e:
                custom_log('RequestFile->try/except. err: ' + str(e))
                return JsonResponse({'message': 'RequestFile->try/except. err: ' + str(e)})
        else:
            return JsonResponse({'message': 'not allowed, sk'})


class RequestHandler(threading.Thread):
    def __init__(self, user, file_page_link_list, data_track):
        super().__init__()
        self.user = user
        self.file_page_link_list = file_page_link_list
        self.data_track = data_track

    def run(self):
        try:
            new_user_request_history = UserRequestHistory.objects.create(user=self.user, data_track=json.dumps(self.data_track))
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
