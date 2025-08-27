from typing import Any, Dict
import zoneinfo
from datetime import timedelta, datetime, time

from django.utils import timezone, dateparse
from django.shortcuts import render, redirect
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect, Http404, HttpResponseForbidden
from django.urls import reverse
from django.views.decorators.http import require_POST
from django.views.generic.list import ListView
from django.db.models import Sum

from babycare import models
from babycare.modelforms import (
    FeedingForm, BreastBumpingForm, BodyTemperatureForm, GrowthDataForm, BabyDateForm)
from iuser.decorators import login_or_404
from utils.datetime import get_local_date, get_range_of_date


# Create your views here.
@login_or_404
def index(request: HttpRequest) -> HttpResponse:
    """
    Render the index page of the baby care dashboard.
    """
    yesterday = get_local_date(timezone.now()) - timedelta(days=1)
    yesterday_range = get_range_of_date(yesterday)
    last_feeding = models.Feeding.objects.filter(
        feed_at__range=yesterday_range)
    last_feeding_amount = sum(map(lambda x: x.amount, last_feeding))
    last_body_temperature = models.BodyTemperature.objects.latest("measure_at")
    last_growth_data = models.GrowthData.objects.latest("date")
    context = {
        'active': 'babycare',
        'last_feeding_amount': last_feeding_amount,
        "last_body_temperature": last_body_temperature,
        "last_growth_data": last_growth_data,
    }
    return render(request, 'babycare/index.html', context)

@login_or_404
def create_baby_date(request: HttpRequest) -> HttpResponse:
    """
    Render the baby date creation page.
    """
    context = dict()
    context['active'] = 'babycare'
    if request.method == 'GET':
        context['form'] = BabyDateForm()
        return render(request, 'babycare/baby_date_create.html', context)
    elif request.method == 'POST':
        form = BabyDateForm(request.POST)
        if form.is_valid():
            babydate = form.save()
            models.BabyRelation.objects.create(
                baby_date=babydate,
                request_by=request.user,
                approve_by=request.user,
                approve_at=timezone.now(),
                status=models.BabyRelation.REQUEST_STATUS[2][0],
            )
            return redirect('dashboard:index')
        else:
            print(form.errors)
    raise Http404()

@require_POST
def fetch_submit_feeding(request: HttpRequest) -> HttpResponse:
    """
    Handle the submission of feeding data via AJAX.
    """
    form = FeedingForm(request.POST)
    if form.is_valid():
        feeding = form.save(commit=False)
        relation = models.BabyRelation.objects.filter(
            baby_date=feeding.baby_date,
            request_by=request.user,
            status__in=models.BabyRelation.feedable_status(),
        ).exists()
        if relation:
            feeding.save()
        else:
            return HttpResponseForbidden()
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
        relation = models.BabyRelation.objects.filter(
            baby_date=breast_bumping.baby_date,
            request_by=request.user,
            status__in=models.BabyRelation.feedable_status(),
        ).exists()
        if relation:
            breast_bumping.save()
        else:
            return HttpResponseForbidden()
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
        relation = models.BabyRelation.objects.filter(
            baby_date=body_temperature.baby_date,
            request_by=request.user,
            status__in=models.BabyRelation.feedable_status(),
        ).exists()
        if relation:
            body_temperature.save()
        else:
            return HttpResponseForbidden()
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
        relation = models.BabyRelation.objects.filter(
            baby_date=growth_data.baby_date,
            request_by=request.user,
            status__in=models.BabyRelation.feedable_status(),
        ).exists()
        if relation:
            growth_data.save()
        else:
            return HttpResponseForbidden()
    else:
        print(form.errors)
    url = reverse('dashboard:index')
    url += f'?babycare_active=growth-data'
    return HttpResponseRedirect(url)


@login_or_404
def feeding_list(request: HttpRequest):
    feed_date_str = request.GET.get('date', '')
    feed_date = dateparse.parse_date(feed_date_str)
    if feed_date is None:
        feed_date = timezone.localdate()
    context: Dict[str, Any] = {'feed_date': feed_date}
    context['previous_day'] = feed_date - timedelta(1)
    if feed_date < timezone.localdate():
        context['next_day'] = feed_date + timedelta(1)
    context['feedings'] = feedings = models.Feeding.objects.filter(baby_date__isnull=False).filter(
        feed_at__range=get_range_of_date(feed_date)).order_by('-feed_at')
    if feedings:
        context['feedings_total'] = feedings.aggregate(Sum('amount'))
    context['active'] = 'babycare'
    return render(request, 'babycare/feedings_list.html', context)


class BodyTemperatureListView(ListView):
    """
    View to list all body temperatures.
    """
    model = models.BodyTemperature
    template_name = 'babycare/body_temperatures_list.html'
    context_object_name = 'body_temperatures'
    paginate_by = 8

    def get_queryset(self):
        return models.BodyTemperature.objects.filter(baby_date__isnull=False).order_by('-measure_at')

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
