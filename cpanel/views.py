import time
import uuid

import jdatetime
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.shortcuts import render, redirect
from django.views import View
import psutil
from django.http import JsonResponse

from accounts.models import RedeemDownloadToken, Profile, MultiToken, UserRedeemHistory, token_generator
from utilities.http_metod import fetch_data_from_http_post


class DashboardView(View):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.context = {}

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            users = User.objects.filter().order_by('id')
            self.context['users'] = users
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
        self.context = {}

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            users = User.objects.filter().order_by('id')
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
        self.context = {}

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            redeem_codes = RedeemDownloadToken.objects.filter()
            paginator = Paginator(redeem_codes, 50)  # Show 25 contacts per page.

            page_number = request.GET.get("page")
            page_obj = paginator.get_page(page_number)

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
            form_type = fetch_data_from_http_post(request, 'form_type', self.context)

            if form_type == 'new_redeem_code_form':
                token_name = fetch_data_from_http_post(request, 'token_name', self.context)
                token_type = fetch_data_from_http_post(request, 'token_type', self.context)
                tokens_count = fetch_data_from_http_post(request, 'tokens_count', self.context)
                expiry_days = fetch_data_from_http_post(request, 'expiry_days', self.context)

                try:
                    tokens_count = int(tokens_count)
                except:
                    self.context['alert'] = 'تعداد توکن بدرستی وارد نشده است'
                    return render(request, 'cpanel/redeem-codes.html', self.context)
                try:
                    expiry_days = int(expiry_days)
                except:
                    self.context['alert'] = 'روزهای انقضا بدرستی وارد نشده است'
                    return render(request, 'cpanel/redeem-codes.html', self.context)

                bulk_creation = fetch_data_from_http_post(request, 'bulk_creation', self.context)
                bulk_creation_number = fetch_data_from_http_post(request, 'bulk_creation_number', self.context)
                belong_to_user = fetch_data_from_http_post(request, 'belong_to_user', self.context)

                if bulk_creation == 'checked':
                    try:
                        bulk_creation_number = int(bulk_creation_number)
                    except:
                        self.context['alert'] = 'تعداد ساخت توکن ها بدرستی وارد نشده است'
                        return render(request, 'cpanel/redeem-codes.html', self.context)
                    for number in range(0, int(bulk_creation_number)):
                        new_token = RedeemDownloadToken.objects.create(
                            token_name=token_name,
                            token_type=token_type,
                            token_unique_code=token_generator(),
                            tokens_count=int(tokens_count),
                            is_used=False,
                            expiry_days=int(expiry_days),
                        )
                else:
                    try:
                        profile = Profile.objects.get(user__id=belong_to_user)
                    except:
                        self.context['alert'] = 'کاربر توکن بدرستی وارد نشده است'
                        return render(request, 'cpanel/redeem-codes.html', self.context)
                    new_token = RedeemDownloadToken.objects.create(
                        token_name=token_name,
                        token_type=token_type,
                        token_unique_code=token_generator(),
                        tokens_count=int(tokens_count),
                        is_used=True,
                        expiry_days=int(expiry_days),
                    )
                    if token_type == 'single':
                        # for i in range(0, new_token.tokens_count):
                        #     new_single_token = SingleToken.objects.create(
                        #         is_used=False,
                        #         expiry_date=jdatetime.datetime.now() + jdatetime.timedelta(
                        #             days=new_token.expiry_days),
                        #     )
                        #     profile.single_tokens.add(new_single_token)
                        pass
                    else:
                        new_multi_token = MultiToken.objects.create(
                            is_used=False,
                            daily_count=new_token.tokens_count,
                            expiry_date=jdatetime.datetime.now() + jdatetime.timedelta(days=new_token.expiry_days),
                        )
                        profile.multi_token = new_multi_token
                    profile.save()
                    new_user_redeem_history = UserRedeemHistory.objects.create(
                        user=profile.user,
                        redeemed_token=new_token,
                    )
                return redirect('cpanel:redeem-codes')
            if form_type == 'edit_redeem_code_form':
                token_id = fetch_data_from_http_post(request, 'token_id', self.context)
                belong_to_user = fetch_data_from_http_post(request, 'belong_to_user', self.context)
                try:
                    profile = Profile.objects.get(user__id=belong_to_user)
                except:
                    self.context['alert'] = 'کاربر توکن بدرستی وارد نشده است'
                    return render(request, 'cpanel/redeem-codes.html', self.context)
                try:
                    redeem_token = RedeemDownloadToken.objects.get(id=token_id)
                except:
                    self.context['alert'] = 'توکن بدرستی انتخاب نشده است'
                    return render(request, 'cpanel/redeem-codes.html', self.context)
                if redeem_token.token_type == 'single':
                    # for i in range(0, redeem_token.tokens_count):
                    #     new_single_token = SingleToken.objects.create(
                    #         is_used=False,
                    #         expiry_date=jdatetime.datetime.now() + jdatetime.timedelta(
                    #             days=redeem_token.expiry_days),
                    #     )
                    #     profile.single_tokens.add(new_single_token)
                    pass
                else:
                    new_multi_token = MultiToken.objects.create(
                        is_used=False,
                        daily_count=redeem_token.tokens_count,
                        expiry_date=jdatetime.datetime.now() + jdatetime.timedelta(days=redeem_token.expiry_days),
                    )
                    profile.multi_token = new_multi_token
                profile.save()
                redeem_token.is_used = True
                redeem_token.save()
                new_user_redeem_history = UserRedeemHistory.objects.create(
                    user=profile.user,
                    redeemed_token=redeem_token,
                )
                return redirect('cpanel:redeem-codes')
            if form_type == 'submit_redeem_code_to_user_form':
                token_unique_code = fetch_data_from_http_post(request, 'token_unique_code', self.context)
                token_belong_to_user = fetch_data_from_http_post(request, 'token_belong_to_user', self.context)
                try:
                    profile = Profile.objects.get(user__id=token_belong_to_user)
                except:
                    self.context['alert'] = 'کاربر توکن بدرستی وارد نشده است'
                    return render(request, 'cpanel/redeem-codes.html', self.context)
                try:
                    redeem_token = RedeemDownloadToken.objects.get(token_unique_code=token_unique_code)
                except:
                    self.context['alert'] = 'شناسه توکن بدرستی وارد نشده است'
                    return render(request, 'cpanel/redeem-codes.html', self.context)
                if redeem_token.token_type == 'single':
                    # for i in range(0, redeem_token.tokens_count):
                    #     new_single_token = SingleToken.objects.create(
                    #         is_used=False,
                    #         expiry_date=jdatetime.datetime.now() + jdatetime.timedelta(days=redeem_token.expiry_days),
                    #     )
                    #     profile.single_tokens.add(new_single_token)
                    pass
                else:
                    new_multi_token = MultiToken.objects.create(
                        is_used=False,
                        daily_count=redeem_token.tokens_count,
                        expiry_date=jdatetime.datetime.now() + jdatetime.timedelta(days=redeem_token.expiry_days),
                    )
                    profile.multi_token = new_multi_token
                profile.save()
                redeem_token.is_used = True
                redeem_token.save()
                new_user_redeem_history = UserRedeemHistory.objects.create(
                    user=profile.user,
                    redeemed_token=redeem_token,
                )
                return redirect('accounts:profile-redeem-history-with-user-id', user_id=token_belong_to_user)
            return render(request, '404.html')
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
                    redeem_code = RedeemDownloadToken.objects.get(id=redeem_code_id)
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