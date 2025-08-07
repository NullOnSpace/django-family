from django.shortcuts import render
from django.contrib.auth.views import LoginView, LogoutView

from . import forms

# Create your views here.
class MyLoginView(LoginView):
    template_name = 'iuser/login.html'
    redirect_authenticated_user = True
    next_page = 'dashboard:index'  # Redirect to dashboard after login
    form_class = forms.UserLoginForm


class MyLogoutView(LogoutView):
    next_page = 'login'  # Redirect to login page after logout
    template_name = 'iuser/logout.html'  # Optional: specify a template for logout confirmation