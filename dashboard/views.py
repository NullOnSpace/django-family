from django.shortcuts import render
from django.http import HttpRequest, HttpResponse, Http404

from babycare.models import BabyDate, Feeding, BreastBumping, BodyTemperature, GrowthData
from babycare.modelforms import FeedingForm, BreastBumpingForm, BodyTemperatureForm, GrowthDataForm
from task_calendar.models import TaskCalendar
from task_calendar.modelforms import TaskCalendarForm
from shopping_list.models import ShoppingList


def index(request: HttpRequest) -> HttpResponse:
    """
    Render the index page of the dashboard.

    This view handles the request to the dashboard's main page and returns
    the rendered HTML template.
    """
    if request.user.is_anonymous:
        return render(request, 'dashboard/public_index.html')
    context = dict()
    context['baby_date'] = BabyDate.objects.first()
    context['task_calendars'] = TaskCalendar.objects.all().order_by('-start_date')
    context['task_form'] = TaskCalendarForm()
    context['shopping_lists'] = ShoppingList.get_recent_lists()
    context['feedings'] = Feeding.get_recent_feedings()
    context['feeding_form'] = FeedingForm()
    context['breast_bumps'] = BreastBumping.objects.all().order_by('-date')
    context['breast_bumping_form'] = BreastBumpingForm()
    context['body_temperatures'] = BodyTemperature.objects.all().order_by('-date')
    context['body_temperature_form'] = BodyTemperatureForm()
    context['growth_data'] = GrowthData.objects.all().order_by('-date')
    context['growth_data_form'] = GrowthDataForm()
    context['active'] = 'index'  # Set the active tab for the navigation bar
    if request.GET.get('babycare_active'):
        context['babycare_active'] = request.GET.get('babycare_active')
    else:
        context['babycare_active'] = 'baby-feeding'
    return render(request, 'dashboard/index.html', context)
