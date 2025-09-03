from typing import Any, Dict
from datetime import timedelta

from django.utils import timezone, dateparse, decorators
from django.shortcuts import render, redirect
from django.http import HttpRequest, HttpResponse, HttpResponseBadRequest, HttpResponseRedirect, Http404, HttpResponseForbidden
from django.urls import reverse
from django.views.decorators.http import require_POST
from django.views.generic.list import ListView
from django.db.models import Sum
from django.contrib.messages import add_message, constants as messages
from django.utils.html import escape

from babycare import models
from babycare.modelforms import (
    FeedingForm, BreastBumpingForm, BodyTemperatureForm, GrowthDataForm, BabyDateForm)
from iuser.decorators import login_or_404
from utils.datetime import get_local_date, get_range_of_date


# Create your views here.
@login_or_404
def index(request: HttpRequest) -> HttpResponse:
    context = dict()
    context['active'] = 'babycare'

    guardianings = models.BabyRelation.objects.filter(
        request_by=request.user, 
        status=models.BabyRelation.REQUEST_STATUS[2][0]
    )
    for guardianing in guardianings:
        to_approve = models.BabyRelation.objects.filter(
            baby_date=guardianing.baby_date,
            status=models.BabyRelation.REQUEST_STATUS[0][0]
        )
        if context.get('to_approve') is None:
            context['to_approve'] = to_approve
        else:
            to_approve.union(models.BabyRelation.objects.filter(
                baby_date=guardianing.baby_date,
                status=models.BabyRelation.REQUEST_STATUS[0][0]
            ))

    context['babies'] = babies = []
    baby_dates = models.BabyRelation.objects.filter(
        request_by=request.user,
        status__in=models.BabyRelation.accessible_status(),
    ).values_list('baby_date__id', 'baby_date__nickname')
    for baby_date_id, nickname in baby_dates:
        feedings = models.Feeding.objects.filter(
            baby_date=baby_date_id)
        if feedings.exists():
            last_feeding = feedings.latest()
            last_feeding_date = get_local_date(last_feeding.feed_at)
            last_feeding_day_range = get_range_of_date(last_feeding_date)
            last_feedings = models.Feeding.objects.filter(
                feed_at__range=last_feeding_day_range)
            last_feedings_amount = sum(map(lambda x: x.amount, last_feedings))
        else:
            last_feedings_amount = None
            last_feeding_date = None
        body_temperatures = models.BodyTemperature.objects.filter(
            baby_date=baby_date_id)
        if body_temperatures.exists():
            last_body_temperature = body_temperatures.latest()
            last_body_temperature_date = get_local_date(
                last_body_temperature.measure_at)
        else:
            last_body_temperature = None
            last_body_temperature_date = None
        growth_data = models.GrowthData.objects.filter(
            baby_date=baby_date_id,
        )
        if growth_data.exists():
            last_growth_data = growth_data.latest()
        else:
            last_growth_data = None
        babies.append((baby_date_id, nickname, last_feedings_amount, last_feeding_date, last_body_temperature, last_body_temperature_date, last_growth_data))
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


@login_or_404
def baby_date_relate_request(request: HttpRequest) -> HttpResponse:
    if request.method == 'GET':
        return render(request, 'babycare/baby_date_relate_request.html')
    elif request.method == 'POST':
        nickname = request.POST.get('nickname')
        nickname = "" if nickname is None else nickname.strip()
        if nickname:
            baby_date = models.BabyDate.objects.filter(nickname=nickname).first()
            if baby_date is not None:
                obj, created = models.BabyRelation.objects.get_or_create(
                    baby_date=baby_date, 
                    request_by=request.user,
                    )
                if created:
                    add_message(
                        request, 
                        messages.SUCCESS, 
                        f'已申请关联 {nickname}'
                    )
                else:
                    add_message(
                        request, 
                        messages.WARNING, 
                        f'已申请过关联 {nickname}'
                    )
                return redirect('babycare:index')
        nickname = escape(nickname)
        add_message(request, messages.ERROR, f'没有找到名为{nickname}的宝宝')
        return redirect('babycare:index')
    else:
        return HttpResponseBadRequest()


@require_POST
def approve_baby_date_relate_request(request: HttpRequest) -> HttpResponse:
    status = request.POST.get('status', "")
    if status.isdigit():
        status = int(status)
        if status not in models.BabyRelation.granted_status():
            # 是数字且不在授权后的状态视为恶意请求
            return HttpResponseBadRequest()
        print(request.POST)
        baby_relation_id = request.POST.get('baby_relation_id', "")
        if baby_relation_id.isdigit():
            baby_relation_id = int(baby_relation_id)
        else:
            return HttpResponseBadRequest()
        relation = models.BabyRelation.objects.filter(
            id=baby_relation_id,
            status__in=models.BabyRelation.pending_status(),
        ).first()
        if relation is not None:
            if relation.can_be_approved_by(request.user):
                if status in models.BabyRelation.reject_status():
                    relation.delete()
                else:
                    relation.status = status
                    relation.approve_by = request.user
                    relation.approve_at = timezone.now()
                    relation.save()
                add_message(
                    request, 
                    messages.SUCCESS, 
                    f'已处理{relation.request_by.username}和{relation.baby_date.nickname}关联'
                )
                return redirect('babycare:index')
            else:
                """该用户无权处理"""
                return HttpResponseForbidden()
        else:
            """该关联不存在或状态已经不是待处理"""
            add_message(
                request,
                messages.WARNING,
                '该关联请求已经由别人处理'
            )
            return redirect('babycare:index')
    else:
        # 状态不正确 可能是默认的空选项
        add_message(
            request,
            messages.WARNING,
            '请选择正确的处理方式'
        )
        return redirect('babycare:index')


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
            status__in=models.BabyRelation.editable_status(),
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
            status__in=models.BabyRelation.editable_status(),
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
            status__in=models.BabyRelation.editable_status(),
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
            status__in=models.BabyRelation.editable_status(),
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
def feeding_list(request: HttpRequest, baby_date_id: int):
    feed_date_str = request.GET.get('date', '')
    feed_date = dateparse.parse_date(feed_date_str)
    if feed_date is None:
        feed_date = timezone.localdate()
    context: Dict[str, Any] = {'feed_date': feed_date}
    context['previous_day'] = feed_date - timedelta(1)
    if feed_date < timezone.localdate():
        context['next_day'] = feed_date + timedelta(1)
    context['feedings'] = feedings = models.Feeding.objects.filter(baby_date=baby_date_id).filter(
        feed_at__range=get_range_of_date(feed_date)).order_by('-feed_at')
    if feedings:
        context['feedings_total'] = feedings.aggregate(Sum('amount'))
    context['active'] = 'babycare'
    return render(request, 'babycare/feedings_list.html', context)


decorators.method_decorator(login_or_404, name='dispatch')
class BodyTemperatureListView(ListView):
    """
    View to list all body temperatures.
    """
    model = models.BodyTemperature
    template_name = 'babycare/body_temperatures_list.html'
    context_object_name = 'body_temperatures'
    paginate_by = 8

    def get_queryset(self):
        return models.BodyTemperature.objects.filter(baby_date=self.kwargs['baby_date_id']).order_by('-measure_at')

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['active'] = 'babycare'
        return context


decorators.method_decorator(login_or_404, name='dispatch')
class GrowthDataListView(ListView):
    """
    View to list all growth data.
    """
    model = models.GrowthData
    template_name = 'babycare/growth_datas_list.html'
    context_object_name = 'growth_data'
    paginate_by = 10

    def get_queryset(self):
        return models.GrowthData.objects.filter(baby_date=self.kwargs['baby_date_id']).order_by('-date')

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['active'] = 'babycare'
        return context
