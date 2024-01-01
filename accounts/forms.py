from django import forms
from captcha.fields import CaptchaField, CaptchaTextInput


class CustomCaptchaTextInput(CaptchaTextInput):
    template_name = 'captcha/captcha_widget.html'


class CaptchaForm(forms.Form):
    captcha = CaptchaField(label="", widget=CustomCaptchaTextInput(
        attrs={'class': 'form-control', 'placeholder': 'عبارت کپچا را وارد نمایید',
               'template_name': 'captcha/captcha_widget.html'}))
