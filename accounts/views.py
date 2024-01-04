import jdatetime
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.views import View
import re

from accounts.forms import CaptchaForm
from accounts.models import UserFileHistory, UserRedeemHistory
from utilities.http_metod import fetch_data_from_http_post, fetch_single_file_from_http_files_data


def login_view(request):
    context = {'page_title': 'ورود به حساب کاربری - مکسیم'}
    if request.user.is_authenticated:
        return redirect('cpanel:dashboard')
    else:
        form = CaptchaForm()
        context['form'] = form
        if request.method == 'POST':
            form = CaptchaForm(request.POST)
            if not form.is_valid():
                context['alert'] = 'کپچا صحیح نمی باشد'
                return render(request, 'account/sign-in.html', context)
            try:
                username = request.POST['username']
                if username == '':
                    username = None
            except:
                username = None
            if username is None:
                context['alert'] = 'نام کاربری بدرستی وارد نشده است'
                return render(request, 'account/sign-in.html', context)
            try:
                password = request.POST['password']
                if password == '':
                    password = None
            except:
                password = None
            if password is None:
                context['username'] = username
                context['alert'] = 'کلمه عبور بدرستی وارد نشده است'
                return render(request, 'account/sign-in.html', context)

            user = authenticate(request=request, username=username, password=password)
            if user is not None:
                if user.is_superuser:
                    login(request=request, user=user)
                    return redirect('cpanel:dashboard')
                else:
                    context['alert'] = 'اجازه دسترسی به این پنل وجود ندارد'
                    return render(request, 'account/sign-in.html', context)
            else:
                try:
                    user = User.objects.get(username=username)
                    context['username'] = username
                    context['alert'] = 'کلمه عبور صحیح نیست'
                    return render(request, 'account/sign-in.html', context)
                except:
                    context['username'] = username
                    context['alert'] = 'نام کاربری در سامانه وجود ندارد'
                    return render(request, 'account/sign-in.html', context)
        return render(request, 'account/sign-in.html', context)


def logout_view(request):
    logout(request=request)
    return redirect('accounts:login')


class ProfileView(View):
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
                self.context['user_by_id'] = user_by_id
            except:
                return render(request, '404.html')
            user_file_history = UserFileHistory.objects.filter(user=user_by_id)
            self.context['user_file_history'] = user_file_history

            single_tokens = user_by_id.user_profile.single_tokens.filter()

            active_tokens = []
            unused_inactive_tokens = []
            for single_token in single_tokens:
                if not single_token.is_used:
                    if single_token.expiry_date > jdatetime.datetime.now():
                        active_tokens.append(single_token)
                        continue
                if single_token.is_used:
                    unused_inactive_tokens.append(single_token)
                    continue
                if single_token.expiry_date < jdatetime.datetime.now():
                    unused_inactive_tokens.append(single_token)
                    continue
            self.context['active_tokens'] = len(active_tokens)
            self.context['unused_inactive_tokens'] = len(unused_inactive_tokens)

            active_multiple_token = []
            if user_by_id.user_profile.multi_token:
                if user_by_id.user_profile.multi_token.expiry_date > jdatetime.datetime.now():
                    active_multiple_token.append(user_by_id.user_profile.multi_token)
            self.context['active_multiple_token'] = active_multiple_token
            return render(request, 'account/profile.html', self.context)
        else:
            return redirect('accounts:login')

    def post(self, request, user_id, *args, **kwargs):
        if request.user.is_authenticated:
            try:
                if not request.user.id == user_id:
                    if not request.user.is_superuser:
                        return render(request, '404.html')
                user_by_id = User.objects.get(id=user_id)
                self.context['user_by_id'] = user_by_id
            except:
                return render(request, '404.html')
        else:
            return redirect('accounts:login')


class ProfileEditView(View):
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
                self.context['user_by_id'] = user_by_id
            except:
                return render(request, '404.html')
            return render(request, 'account/profile-edit.html', self.context)
        else:
            return redirect('accounts:login')

    def post(self, request, user_id, *args, **kwargs):
        if request.user.is_authenticated:
            try:
                if not request.user.id == user_id:
                    if not request.user.is_superuser:
                        return render(request, '404.html')
                user_by_id = User.objects.get(id=user_id)
                self.context['user_by_id'] = user_by_id
            except:
                return render(request, '404.html')
            user_file_history = UserFileHistory.objects.filter(user=user_by_id)
            self.context['user_file_history'] = user_file_history

            form_name = fetch_data_from_http_post(request, 'form_name', self.context)

            if form_name == 'profile_edit_form':
                full_name = fetch_data_from_http_post(request, 'full_name', self.context)
                telegram_mobile_phone_number = fetch_data_from_http_post(request, 'telegram_mobile_phone_number',
                                                                         self.context)
                user_daily_limit = fetch_data_from_http_post(request, 'user_daily_limit', self.context)
                profile_pic = fetch_single_file_from_http_files_data(request, 'avatar', self.context)

                try:
                    user_daily_limit = int(user_daily_limit)
                except:
                    return JsonResponse({'alert': 'تعداد درخواست های مجاز روزانه صحیح نیست'})

                user = user_by_id
                if full_name:
                    user.first_name = full_name
                user.save()

                user_profile = user_by_id.user_profile

                if telegram_mobile_phone_number:
                    user_profile.user_telegram_phone_number = telegram_mobile_phone_number
                if user_daily_limit:
                    user_profile.daily_limit = int(user_daily_limit)
                if profile_pic:
                    user_profile.profile_pic = profile_pic
                user_profile.save()
                return JsonResponse({'message': 'با موفقیت ذخیره شد'})

            if form_name == 'user_auth_form':
                new_password = fetch_data_from_http_post(request, 'password', self.context)
                if new_password:
                    if len(str(new_password)) >= 8:
                        user = user_by_id
                        user.set_password(str(new_password))
                        user.save()
                        return JsonResponse({'message': 'با موفقیت ذخیره شد'})
                return JsonResponse({'alert': 'رمز عبور حداقل 8 کاراکتر باشد'})
            return render(request, '404.html')
        else:
            return redirect('accounts:login')


class ProfileDownloadHistoryView(View):
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
                self.context['user_by_id'] = user_by_id
                user_files_history = UserFileHistory.objects.filter(user=user_by_id)
                self.context['user_files_history'] = user_files_history
            except:
                return render(request, '404.html')
            return render(request, 'account/profile-download-history.html', self.context)
        else:
            return redirect('accounts:login')

    def post(self, request, user_id, *args, **kwargs):
        if request.user.is_authenticated:
            try:
                if not request.user.id == user_id:
                    if not request.user.is_superuser:
                        return render(request, '404.html')
                user_by_id = User.objects.get(id=user_id)
                self.context['user_by_id'] = user_by_id
            except:
                return render(request, '404.html')
            return render(request, '404.html')
        else:
            return redirect('accounts:login')


class ProfileRedeemHistoryView(View):
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
                self.context['user_by_id'] = user_by_id
                user_redeem_history = UserRedeemHistory.objects.filter(user=user_by_id)
                self.context['user_redeem_history'] = user_redeem_history
            except:
                return render(request, '404.html')
            return render(request, 'account/profile-redeem-history.html', self.context)
        else:
            return redirect('accounts:login')

    def post(self, request, user_id, *args, **kwargs):
        if request.user.is_authenticated:
            try:
                if not request.user.id == user_id:
                    if not request.user.is_superuser:
                        return render(request, '404.html')
                user_by_id = User.objects.get(id=user_id)
                self.context['user_by_id'] = user_by_id
            except:
                return render(request, '404.html')
            return render(request, '404.html')
        else:
            return redirect('accounts:login')

