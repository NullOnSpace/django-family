from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserChangeForm, UsernameField

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
