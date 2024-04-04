import time
import uuid
from decimal import Decimal
from django.db.models import Q
import jdatetime
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.shortcuts import render, redirect
from django.views import View
import psutil
from django.http import JsonResponse

from accounts.models import Profile, UserMultiToken, token_generator, WalletRedeemToken, ScraperRedeemToken, \
    UserScraperTokenRedeemHistory
from custom_logs.models import custom_log
from utilities.http_metod import fetch_data_from_http_post, fetch_data_from_http_get


class DashboardView(View):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.context = {'page_title': 'داشبورد ادمین'}

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return render(request, 'cpanel/dashboard.html', self.context)
        else:
            return redirect('accounts:login')

    def post(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return render(request, '404.html')
        else:
            return redirect('accounts:login')


def ajax_get_resource_usage(request):
    cpu_usage = psutil.cpu_percent()
    memory_usage = psutil.virtual_memory().percent
    disk_usage = psutil.disk_usage('/').percent

    data = {
        'cpu_usage': cpu_usage,
        'memory_usage': memory_usage,
        'disk_usage': disk_usage,
    }
    print(data)
    return JsonResponse(data)



def get_network_transfer_rate(request):
    # Get the initial bytes sent and received
    initial_net_io = psutil.net_io_counters()
    initial_bytes_sent = initial_net_io.bytes_sent
    initial_bytes_recv = initial_net_io.bytes_recv

    # Wait for the specified interval
    time.sleep(1)

    # Get the final bytes sent and received after the interval
    final_net_io = psutil.net_io_counters()
    final_bytes_sent = final_net_io.bytes_sent
    final_bytes_recv = final_net_io.bytes_recv

    # Calculate the transfer rate in bytes per second for both sent and received
    bytes_sent_per_sec = (final_bytes_sent - initial_bytes_sent) / 1
    bytes_received_per_sec = (final_bytes_recv - initial_bytes_recv) / 1
    data = {
        'bytes_sent_per_sec': bytes_sent_per_sec,
        'bytes_received_per_sec': bytes_received_per_sec,
    }
    return JsonResponse(data)


class UserView(View):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.context = {'page_title': 'اطلاعات کاربر'}

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            users = User.objects.filter(user_profile__isnull=False).order_by('id')
            self.context['users'] = users
            return render(request, 'cpanel/users.html', self.context)
        else:
            return redirect('accounts:login')

    def post(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return render(request, '404.html')
        else:
            return redirect('accounts:login')


class UserRemoveView(View):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.context = {}

    def get(self, request, user_id, *args, **kwargs):
        if request.user.is_authenticated:
            try:
                if not request.user.id == user_id:
                    if not request.user.is_superuser:
                        return render(request, '404.html')
                user_by_id = User.objects.get(id=user_id)
                user_by_id.delete()
                return redirect('cpanel:users')
            except Exception as e:
                print(str(e))
                return render(request, '404.html')
        else:
            return redirect('accounts:login')

    def post(self, request, user_id, *args, **kwargs):
        if request.user.is_authenticated:
            return render(request, '404.html')
        else:
            return redirect('accounts:login')


class RedeemCodeView(View):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.context = {'page_title': 'ردیم توکن'}

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            get_token_type = fetch_data_from_http_get(request, 'get_token_type', self.context)
            get_token_used = fetch_data_from_http_get(request, 'get_token_used', self.context)

            wallet_redeem_tokens = None
            scraper_redeem_tokens = None

            q = Q()
            if get_token_used == 'used':
                q &= Q(**{f'is_used': True})
            if get_token_used == 'not_used':
                q &= Q(**{f'is_used': False})

            if get_token_type == 'wallet':
                wallet_redeem_tokens = WalletRedeemToken.objects.filter(q)
            elif get_token_type == 'envato':
                q &= Q(**{f'token_type': get_token_type})
                scraper_redeem_tokens = ScraperRedeemToken.objects.filter(q)
            elif get_token_type == 'motion_array':
                q &= Q(**{f'token_type': get_token_type})
                scraper_redeem_tokens = ScraperRedeemToken.objects.filter(q)
            else:
                wallet_redeem_tokens = WalletRedeemToken.objects.filter(q)
                scraper_redeem_tokens = ScraperRedeemToken.objects.filter(q)


            redeem_codes = []
            if wallet_redeem_tokens:
                for wallet_redeem_token in wallet_redeem_tokens:
                    redeem_codes.append(wallet_redeem_token)
            if scraper_redeem_tokens:
                for scraper_redeem_token in scraper_redeem_tokens:
                    redeem_codes.append(scraper_redeem_token)
            paginator = Paginator(redeem_codes, 50)  # Show 25 contacts per page.

            page_number = request.GET.get("page")
            page_obj = paginator.get_page(page_number)

            export_list = ''
            for obj in page_obj:
                export_list += f'{obj.id},'

            self.context['export_list'] = export_list
            self.context['page_obj'] = page_obj
            print(page_obj.has_previous())
            print(page_obj.has_next())
            print(page_obj.start_index())
            print(page_obj.end_index())
            users = User.objects.filter()
            self.context['users'] = users
            return render(request, 'cpanel/redeem-codes.html', self.context)
        else:
            return redirect('accounts:login')

    def post(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            token_type = fetch_data_from_http_post(request, 'token_type', self.context)

            wallet_credit = None
            tokens_total_limit = None
            tokens_daily_limit = None
            expiry_days = None
            if token_type == 'wallet':
                wallet_credit = fetch_data_from_http_post(request, 'wallet_credit', self.context)
                if not wallet_credit:
                    self.context['alert'] = 'اعتبار کد بدرستی وارد نشده است'
                    return render(request, 'cpanel/redeem-codes.html', self.context)
            else:
                tokens_total_limit = fetch_data_from_http_post(request, 'tokens_total_limit', self.context)
                tokens_daily_limit = fetch_data_from_http_post(request, 'tokens_daily_limit', self.context)
                expiry_days = fetch_data_from_http_post(request, 'expiry_days', self.context)

                if not tokens_total_limit:
                    self.context['alert'] = 'لیمیت کلی کد بدرستی وارد نشده است'
                    return render(request, 'cpanel/redeem-codes.html', self.context)

                if not tokens_daily_limit:
                    self.context['alert'] = 'لیمیت روزانه کد بدرستی وارد نشده است'
                    return render(request, 'cpanel/redeem-codes.html', self.context)

                if not expiry_days:
                    self.context['alert'] = 'لیمیت زمانی کد بدرستی وارد نشده است'
                    return render(request, 'cpanel/redeem-codes.html', self.context)

            bulk_creation_number = fetch_data_from_http_post(request, 'bulk_creation_number', self.context)

            if not bulk_creation_number:
                self.context['alert'] = 'تعداد کد های در حال ساخت بدرستی وارد نشده است'
                return render(request, 'cpanel/redeem-codes.html', self.context)

            if token_type == 'wallet':
                for i in range(0, int(bulk_creation_number)):
                    WalletRedeemToken.objects.create(
                        charge_amount=Decimal(wallet_credit),
                    )
            else:
                for i in range(0, int(bulk_creation_number)):
                    ScraperRedeemToken.objects.create(
                        token_name=token_type,
                        token_type=token_type,
                        total_tokens=int(tokens_total_limit),
                        daily_allowed_number=int(tokens_daily_limit),
                        expiry_days=int(expiry_days),
                    )
            return redirect('cpanel:redeem-codes')
        else:
            return redirect('accounts:login')


class RemoveRedeemCodeView(View):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.context = {}

    def get(self, request, redeem_code_id, *args, **kwargs):
        if request.user.is_authenticated:
            if request.user.is_superuser:
                try:
                    redeem_code = ScraperRedeemToken.objects.get(id=redeem_code_id)
                    redeem_code.delete()
                except:
                    return render(request, '404.html')
                return redirect('cpanel:redeem-codes')
            else:
                return render(request, '404.html')
        else:
            return redirect('accounts:login')

    def post(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return render(request, '404.html')
        else:
            return redirect('accounts:login')