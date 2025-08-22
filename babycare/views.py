from typing import Any
import zoneinfo
from datetime import timedelta, datetime, time

from django.utils import timezone
from django.shortcuts import render, redirect
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.views.decorators.http import require_POST
from django.views.generic.list import ListView

from babycare import models
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
        feeding.baby_date = models.BabyDate.objects.first()
        feeding.save()
    else:
        print(form.errors)
    url = reverse('dashboard:index')
    url += f'?babycare_active=baby-feeding'
    return HttpResponseRedirect(url)


@require_POST
def fetch_submit_breast_bumping(request: HttpRequest) -> HttpResponse:
    """
    Handle the submission of breast bumping data via AJAX.
    """
    form = BreastBumpingForm(request.POST)
    if form.is_valid():
        breast_bumping = form.save(commit=False)
        # (fixme) babydate应该是和提交用户相关
        breast_bumping.baby_date = models.BabyDate.objects.first()
        breast_bumping.save()
    else:
        print(form.errors)
    url = reverse('dashboard:index')
    url += f'?babycare_active=breast-bumping'
    return HttpResponseRedirect(url)


@require_POST
def fetch_submit_body_temperature(request: HttpRequest) -> HttpResponse:
    """
    Handle the submission of body temperature data via AJAX.
    """
    form = BodyTemperatureForm(request.POST)
    if form.is_valid():
        body_temperature = form.save(commit=False)
        # (fixme) babydate应该是和提交用户相关
        body_temperature.baby_date = models.BabyDate.objects.first()
        body_temperature.save()
    else:
        print(form.errors)
    url = reverse('dashboard:index')
    url += f'?babycare_active=body-temperature'
    return HttpResponseRedirect(url)


@require_POST
def fetch_submit_growth_data(request: HttpRequest) -> HttpResponse:
    """
    Handle the submission of growth data via AJAX.
    """
    form = GrowthDataForm(request.POST)
    if form.is_valid():
        growth_data = form.save(commit=False)
        # (fixme) babydate应该是和提交用户相关
        growth_data.baby_date = models.BabyDate.objects.first()
        growth_data.save()
    else:
        print(form.errors)
    url = reverse('dashboard:index')
    url += f'?babycare_active=growth-data'
    return HttpResponseRedirect(url)


def index(request: HttpRequest) -> HttpResponse:
    """
    Render the index page of the baby care dashboard.
    """
    if request.user.is_anonymous:
        return render(request, 'dashboard/public_index.html')
    tz = zoneinfo.ZoneInfo('Asia/Shanghai')
    yesterday = timezone.now().astimezone(tz).date() - timedelta(days=1)
    yesterday_start = datetime.combine(yesterday, time.min, tzinfo=tz)
    yesterday_end = datetime.combine(yesterday, time.max, tzinfo=tz)
    last_feeding = models.Feeding.objects.filter(date__range=(yesterday_start, yesterday_end))
    last_feeding_amount = sum(map(lambda x: x.amount, last_feeding))
    last_body_temperature = models.BodyTemperature.objects.latest("date")
    last_growth_data = models.GrowthData.objects.latest("date")
    context = {
        'active': 'babycare',
        'last_feeding_amount': last_feeding_amount,
        "last_body_temperature": last_body_temperature,
        "last_growth_data": last_growth_data,
    }
    return render(request, 'babycare/index.html', context)

class FeedingListView(ListView):
    """
    View to list all feedings.
    """
    model = models.Feeding
    template_name = 'babycare/feedings_list.html'
    context_object_name = 'feedings'
    paginate_by = 10

    def get_queryset(self):
        return models.Feeding.objects.filter(baby_date__isnull=False).order_by('-date')
    
    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['active'] = 'babycare'
        return context


class BodyTemperatureListView(ListView):
    """
    View to list all body temperatures.
    """
    model = models.BodyTemperature
    template_name = 'babycare/body_temperatures_list.html'
    context_object_name = 'body_temperatures'
    paginate_by = 8

    def get_queryset(self):
        return models.BodyTemperature.objects.filter(baby_date__isnull=False).order_by('-date')
    
    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['active'] = 'babycare'
        return context
    

class GrowthDataListView(ListView):
    """
    View to list all growth data.
    """
    model = models.GrowthData
    template_name = 'babycare/growth_datas_list.html'
    context_object_name = 'growth_data'
    paginate_by = 10

    def get_queryset(self):
        return models.GrowthData.objects.filter(baby_date__isnull=False).order_by('-date')
    
    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['active'] = 'babycare'
        return context