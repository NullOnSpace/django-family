from django import forms
from django.contrib.auth.forms import AuthenticationForm, UsernameField
from django.core.exceptions import ValidationError

from .models import User


class UserLoginForm(AuthenticationForm):
    username = UsernameField(
        label="用户名",
        strip=True,
        widget=forms.TextInput(
        attrs={"autofocus": True, "class": "form-control"}))
    password = forms.CharField(
        label="密码",
        strip=False,
        widget=forms.PasswordInput(attrs={
            "autocomplete": "current-password",
            "class": "form-control",
        }),
    )

    error_messages = {
        "invalid_login": "用户名或密码错误。",
        "inactive": "该账户未激活。",
    }

class UserRegisterForm(forms.Form):
    username = UsernameField(
        label="用户名",
        strip=True,
        widget=forms.TextInput(
        attrs={"autofocus": True, "class": "form-control"}))
    password1 = forms.CharField(
        label="密码",
        strip=False,
        widget=forms.PasswordInput(attrs={
            "autocomplete": "current-password",
            "class": "form-control",
        }),
    )
    password2 = forms.CharField(
        label="再次输入密码",
        strip=False,
        widget=forms.PasswordInput(attrs={
            "autocomplete": "current-password",
            "class": "form-control",
        }),
    )

    def clean_username(self):
        username = self.cleaned_data['username']
        if User.objects.filter(username=username).exists():
            raise ValidationError("用户名已存在")
        return username

    def clean(self):
        cd = self.cleaned_data
        if cd['password1'] != cd['password2']:
            raise ValidationError("两次输入密码不一致")
        return super().clean()