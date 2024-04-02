import json

import requests

from core.models import get_envato_telegram_bot_config_settings
from custom_logs.models import custom_log


def telegram_http_send_message_via_get_method(chat_id, text):
    try:
        req = requests.get(
            url='https://api.telegram.org/bot' + get_envato_telegram_bot_config_settings().bot_token + '/sendMessage?chat_id=' + str(
                chat_id) + '&text=' + str(text))
        custom_log('telegram_http_send_message_via_get_method-> message: ' + str(json.loads(req.content)))
    except Exception as e:
        custom_log('telegram_http_send_message_via_get_method->try/except. err: ' + str(e))


def telegram_http_send_message_via_post_method(chat_id, text, parse_mode, message_thread_id=None,
                                               entities=None, disable_web_page_preview=None, disable_notification=None,
                                               protect_content=None, reply_to_message_id=None,
                                               allow_sending_without_reply=None, reply_markup=None):
    telegram_api_url = f'https://api.telegram.org/bot{get_envato_telegram_bot_config_settings().bot_token}/sendMessage'
    data = {
        'chat_id': chat_id,
        'message_thread_id': message_thread_id,
        'text': text,
        'parse_mode': parse_mode,
        'entities': entities,
        'disable_web_page_preview': disable_web_page_preview,
        'disable_notification': disable_notification,
        'protect_content': protect_content,
        'reply_to_message_id': reply_to_message_id,
        'allow_sending_without_reply': allow_sending_without_reply,
        'reply_markup': reply_markup,
    }
    try:
        response = requests.post(telegram_api_url, data=data)
        custom_log('telegram_http_send_message_via_post_method-> message: ' + str(json.loads(response.content)))
        response_message = {
            'result': 'success',
            'message': response.text,
        }
    except Exception as e:
        custom_log('telegram_http_send_message_via_post_method->try/except. err: ' + str(e))
        response_message = {
            'result': 'failed',
            'message': str(e),
        }
    return response_message


def telegram_http_update_message_via_post_method(chat_id, message_id, text, parse_mode, inline_message_id=None,
                                                 entities=None, disable_web_page_preview=None, reply_markup=None):
    telegram_api_url = f'https://api.telegram.org/bot{get_envato_telegram_bot_config_settings().bot_token}/editMessageText'
    data = {
        'chat_id': chat_id,
        'message_id': message_id,
        'inline_message_id': inline_message_id,
        'text': text,
        'parse_mode': parse_mode,
        'entities': entities,
        'disable_web_page_preview': disable_web_page_preview,
        'reply_markup': reply_markup,

    }
    try:
        response = requests.post(telegram_api_url, data=data)
        response_json = json.loads(response.content)
        response_message = {
            'result': 'success',
            'message': response.text,
        }
        try:
            if response_json['error_code'] != 400:
                custom_log('telegram_http_update_message_via_post_method-> message: ' + str(json.loads(response.content)))
        except Exception as e:
            custom_log('telegram_http_update_message_via_post_method->try/except on error_code. err: ' + str(e))
    except Exception as e:
        custom_log('telegram_http_update_message_via_post_method->try/except. err: ' + str(e))
        response_message = {
            'result': 'failed',
            'message': str(e),
        }
    return response_message


def telegram_http_send_photo_via_post_method(chat_id, photo, caption, parse_mode, message_thread_id=None,
                                             caption_entities=None,
                                             has_spoiler=None, disable_notification=None, protect_content=None,
                                             reply_to_message_id=None, allow_sending_without_reply=None,
                                             reply_markup=None, ):
    telegram_api_url = f'https://api.telegram.org/bot{get_envato_telegram_bot_config_settings().bot_token}/sendPhoto'
    data = {
        'chat_id': chat_id,
        'message_thread_id': message_thread_id,
        'photo': photo,
        'caption': caption,
        # 'parse_mode': parse_mode,
        # 'caption_entities': caption_entities,
        # 'has_spoiler': has_spoiler,
        # 'disable_notification': disable_notification,
        # 'protect_content': protect_content,
        # 'reply_to_message_id': reply_to_message_id,
        # 'allow_sending_without_reply': allow_sending_without_reply,
        # 'reply_markup': reply_markup,
    }
    try:
        response = requests.post(telegram_api_url, data=data)
        custom_log('telegram_http_send_photo_via_post_method-> message: ' + str(json.loads(response.content)))
        response_message = {
            'result': 'success',
            'message': response.text,
        }
    except Exception as e:
        custom_log('telegram_http_send_photo_via_post_method->try/except. err: ' + str(e))
        response_message = {
            'result': 'failed',
            'message': str(e),
        }
    return response_message
