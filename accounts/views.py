import jdatetime
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.views import View
import re

from accounts.models import UserFileHistory, UserScraperTokenRedeemHistory
from utilities.http_metod import fetch_data_from_http_post, fetch_single_file_from_http_files_data


def login_view(request):
    context = {'page_title': 'ورود به حساب کاربری - مکسیم'}
    if request.user.is_authenticated:
        return redirect('cpanel:dashboard')
    else:
        if request.method == 'POST':
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
        self.context = {'page_title': 'مشخصات حساب کاربری'}

    def get(self, request, user_id, *args, **kwargs):
        if request.user.is_authenticated:
            if not request.user.id == user_id and not request.user.is_superuser:
                return render(request, '404.html')

            try:
                user = User.objects.get(id=user_id)
                self.context['user'] = user
            except:
                return render(request, '404.html')

            user_file_history = UserFileHistory.objects.filter(user=user)
            self.context['user_file_history'] = user_file_history

            return render(request, 'account/profile.html', self.context)
        else:
            return redirect('accounts:login')

    def post(self, request, user_id, *args, **kwargs):
        return JsonResponse({'message': 'not allowed'})


class ProfileEditView(View):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.context = {'page_title': 'ویرایش حساب کاربری'}

    def get(self, request, user_id, *args, **kwargs):
        if request.user.is_authenticated:
            if not request.user.id == user_id and not request.user.is_superuser:
                return render(request, '404.html')

            try:
                user = User.objects.get(id=user_id)
                self.context['user'] = user
            except:
                return render(request, '404.html')
            return render(request, 'account/profile-edit.html', self.context)
        else:
            return redirect('accounts:login')

    def post(self, request, user_id, *args, **kwargs):
        if request.user.is_authenticated:
            if not request.user.id == user_id and not request.user.is_superuser:
                return render(request, '404.html')

            try:
                user = User.objects.get(id=user_id)
                self.context['user'] = user
            except:
                return render(request, '404.html')
            user_file_history = UserFileHistory.objects.filter(user=user)
            self.context['user_file_history'] = user_file_history

            form_name = fetch_data_from_http_post(request, 'form_name', self.context)

            if form_name == 'profile_edit_form':
                full_name = fetch_data_from_http_post(request, 'full_name', self.context)
                telegram_mobile_phone_number = fetch_data_from_http_post(request, 'telegram_mobile_phone_number',
                                                                         self.context)

                if full_name:
                    user.first_name = full_name
                user.save()

                user_profile = user.user_profile

                if telegram_mobile_phone_number:
                    user_profile.user_telegram_phone_number = telegram_mobile_phone_number

                user_profile.save()
                return JsonResponse({'message': 'با موفقیت ذخیره شد'})

            if form_name == 'user_auth_form':
                new_password = fetch_data_from_http_post(request, 'password', self.context)
                if new_password:
                    if len(str(new_password)) >= 8:
                        user = user
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
        self.context = {'page_title': 'تاریخچه دانلود کاربر'}

    def get(self, request, user_id, *args, **kwargs):
        if request.user.is_authenticated:
            if not request.user.id == user_id and not request.user.is_superuser:
                return render(request, '404.html')
            try:
                user = User.objects.get(id=user_id)
                self.context['user'] = user
            except:
                return render(request, '404.html')
            user_files_history = UserFileHistory.objects.filter(user=user)
            self.context['user_files_history'] = user_files_history
            return render(request, 'account/profile-download-history.html', self.context)
        else:
            return redirect('accounts:login')

    def post(self, request, user_id, *args, **kwargs):
        return JsonResponse({'message': 'not allowed'})


class ProfileRedeemHistoryView(View):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.context = {'page_title': 'تاریخچه توکن های ردیم شده کاربر'}

    def get(self, request, user_id, *args, **kwargs):
        if request.user.is_authenticated:
            if not request.user.id == user_id and not request.user.is_superuser:
                return render(request, '404.html')
            try:
                user = User.objects.get(id=user_id)
                self.context['user'] = user
            except:
                return render(request, '404.html')
            user_redeem_history = UserScraperTokenRedeemHistory.objects.filter(user=user)
            self.context['user_redeem_history'] = user_redeem_history
            return render(request, 'account/profile-redeem-history.html', self.context)
        else:
            return redirect('accounts:login')

    def post(self, request, user_id, *args, **kwargs):
        return JsonResponse({'message': 'not allowed'})

