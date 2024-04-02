import time

from django.contrib import admin
from django.contrib.admin.helpers import ACTION_CHECKBOX_NAME
from django.contrib.auth.models import User

from contact.models import Message
from maxim_telegram_bot.settings import BASE_URL
from utilities.telegram_message_handler import telegram_http_send_message_via_post_method


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'created_at_display',
    )

    readonly_fields = (
        'created_at',
    )

    fields = (
        'title',
        'description',
        'file',
        'receivers',
        'created_at',
    )

    @admin.display(description="تاریخ ایجاد", empty_value='???')
    def created_at_display(self, obj):
        data_time = str(obj.created_at.strftime('%y-%m-%d - %H:%M:%S %Z'))
        return data_time

    @admin.action(description='ارسال به همه کاربران')
    def send_message_to_all(self, request, queryset):
        users = User.objects.all()
        for user in users:
            for query in queryset:
                message_text = f''''''
                message_text += f'<b>{query.title}</b>'
                message_text += '\n'
                message_text += f'{query.description}'
                message_text += '\n'
                if query.file:
                    message_text += f'<a href="{BASE_URL}{query.file.url}">فایل ضمیمه</a>'
                    message_text += '\n'
                telegram_http_send_message_via_post_method(chat_id=user.username, text=message_text, parse_mode='HTML')
                time.sleep(1)
            time.sleep(1)

    @admin.action(description='ارسال به کاربران مشخص شده')
    def send_message(self, request, queryset):
        for query in queryset:
            users = query.receivers.all()
            for user in users:
                message_text = f''''''
                message_text += f'<b>{query.title}</b>'
                message_text += '\n'
                message_text += f'{query.description}'
                message_text += '\n'
                if query.file:
                    message_text += f'<a href="{BASE_URL}{query.file.url}">فایل ضمیمه</a>'
                    message_text += '\n'
                telegram_http_send_message_via_post_method(chat_id=user.username, text=message_text, parse_mode='HTML')
                time.sleep(1)
            time.sleep(1)

    actions = (
        'send_message_to_all',
        'send_message',
    )
