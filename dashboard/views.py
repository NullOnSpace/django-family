from django.shortcuts import render
from django.http import HttpRequest, HttpResponse
from django.utils import timezone

from babycare.models import BabyRelation, BabyDate, Feeding, BreastBumping, BodyTemperature, GrowthData, Diaper
from babycare.modelforms import FeedingForm, BreastBumpingForm, BodyTemperatureForm, GrowthDataForm, DiaperForm
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
    context['active'] = 'index'  # Set the active tab for the navigation bar
    context['task_calendars'] = TaskCalendar.objects.all().order_by('-start_date')
    context['task_form'] = TaskCalendarForm()
    context['shopping_lists'] = ShoppingList.get_recent_lists()
    context['babycare_active'] = request.GET.get(
        'babycare_active', 'baby-feeding')

    if request.session.get_expiry_age() <= 7*24*3600:
        request.session.set_expiry(7 * 24 * 3600)

    baby_dates = BabyRelation.objects.filter(
        request_by=request.user,
        status__in=BabyRelation.accessible_status()
    ).values_list('baby_date', flat=True)
    context['babies'] = babies = []
    for baby_date in BabyDate.objects.filter(id__in=baby_dates):
        baby = dict()
        baby['baby_date'] = baby_date

        baby['feedings'] = Feeding.get_recent_feedings(baby_date.pk)
        baby['feeding_form'] = FeedingForm(initial={'baby_date': baby_date.pk})
            
        baby['body_temperatures'] = BodyTemperature.get_recent_temp(
            baby_date.pk)
        baby['body_temperature_form'] = BodyTemperatureForm(
            initial={'baby_date': baby_date.pk})
        
        baby['growth_data'] = GrowthData.get_recent_growth_data(baby_date.pk)
        baby['growth_data_form'] = GrowthDataForm(
            initial={'baby_date': baby_date.pk})

        baby['diapers'] = Diaper.get_recent_diapers(baby_date.id)
        baby['diaper_form'] = DiaperForm(
            initial={'baby_date': baby_date.pk}
        )

        babies.append(baby)
    return render(request, 'dashboard/index.html', context)
