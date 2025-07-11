from django.shortcuts import render
from django.http import HttpRequest, HttpResponse

from babycare.models import BabyDate
from task_calendar.models import TaskCalendar
from shopping_list.models import ShoppingList


def index(request: HttpRequest) -> HttpResponse:
    """
    Render the index page of the dashboard.

    This view handles the request to the dashboard's main page and returns
    the rendered HTML template.
    """
    baby_date = BabyDate.objects.first()
    task_calendars = TaskCalendar.objects.all()
    shopping_lists = ShoppingList.objects.all()
    return render(request, 'dashboard/index.html', {'baby_date': baby_date, 'task_calendars': task_calendars, "shopping_lists": shopping_lists})
