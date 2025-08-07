from django.shortcuts import render, redirect
from django.http import HttpRequest, HttpResponse
from django.views.decorators.http import require_POST

from babycare.models import BabyDate
from babycare.modelforms import (
    FeedingForm, BreastBumpingForm, BodyTemperatureForm, GrowthDataForm)


# Create your views here.
@require_POST
def fetch_submit_feeding(request: HttpRequest) -> HttpResponse:
    """
    Handle the submission of feeding data via AJAX.
    """
    form = FeedingForm(request.POST)
    if form.is_valid():
        feeding = form.save(commit=False)
        # (fixme) babydate应该是和提交用户相关
        feeding.baby_date = BabyDate.objects.first()
        feeding.save()
    else:
        print(form.errors)
    return redirect('dashboard:index')


@require_POST
def fetch_submit_breast_bumping(request: HttpRequest) -> HttpResponse:
    """
    Handle the submission of breast bumping data via AJAX.
    """
    form = BreastBumpingForm(request.POST)
    if form.is_valid():
        breast_bumping = form.save(commit=False)
        # (fixme) babydate应该是和提交用户相关
        breast_bumping.baby_date = BabyDate.objects.first()
        breast_bumping.save()
    else:
        print(form.errors)
    return redirect('dashboard:index')


@require_POST
def fetch_submit_body_temperature(request: HttpRequest) -> HttpResponse:
    """
    Handle the submission of body temperature data via AJAX.
    """
    form = BodyTemperatureForm(request.POST)
    if form.is_valid():
        body_temperature = form.save(commit=False)
        # (fixme) babydate应该是和提交用户相关
        body_temperature.baby_date = BabyDate.objects.first()
        body_temperature.save()
    else:
        print(form.errors)
    return redirect('dashboard:index')


@require_POST
def fetch_submit_growth_data(request: HttpRequest) -> HttpResponse:
    """
    Handle the submission of growth data via AJAX.
    """
    form = GrowthDataForm(request.POST)
    if form.is_valid():
        growth_data = form.save(commit=False)
        # (fixme) babydate应该是和提交用户相关
        growth_data.baby_date = BabyDate.objects.first()
        growth_data.save()
    else:
        print(form.errors)
    return redirect('dashboard:index')
