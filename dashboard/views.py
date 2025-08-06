from django.shortcuts import render
from django.http import HttpRequest, HttpResponse

from babycare.models import BabyDate
from task_calendar.models import TaskCalendar
from task_calendar.modelforms import TaskCalendarForm
from shopping_list.models import ShoppingList


def index(request: HttpRequest) -> HttpResponse:
    """
    Render the index page of the dashboard.

    This view handles the request to the dashboard's main page and returns
    the rendered HTML template.
    """
    context = dict()
    context['baby_date'] = BabyDate.objects.first()
    context['task_calendars'] = TaskCalendar.objects.all().order_by('-start_date')
    context['task_form'] = TaskCalendarForm()
    context['shopping_lists'] = ShoppingList.objects.all()
    return render(request, 'dashboard/index.html', context)
