from django.shortcuts import render, redirect
from django.contrib.auth.views import LoginView, LogoutView
from django.views.generic.edit import CreateView
from django.contrib import auth
from django.views.decorators.http import require_http_methods


from . import forms, models

# Create your views here.
class MyLoginView(LoginView):
    template_name = 'iuser/login.html'
    redirect_authenticated_user = True
    next_page = 'dashboard:index'  # Redirect to dashboard after login
    form_class = forms.UserLoginForm


class MyLogoutView(LogoutView):
    next_page = 'login'  # Redirect to login page after logout
    template_name = 'iuser/logout.html'  # Optional: specify a template for logout confirmation


@require_http_methods(["GET", "POST"])
def user_register(request):
    context = dict()
    if request.method == "GET":
        context['form'] = forms.UserRegisterForm()
        return render(request, 'iuser/register.html', context)
    else:
        context['form'] = form = forms.UserRegisterForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            user = models.User(username=cd['username'])
            user.set_password(cd['password1'])
            user.save()
            auth.login(request, user)
            return redirect('dashboard:index')
        else:
            return render(request, 'iuser/register.html', context)
