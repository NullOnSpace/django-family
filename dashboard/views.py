from django.shortcuts import render
from django.http import HttpRequest, HttpResponse

from babycare.models import BabyDate


def index(request: HttpRequest) -> HttpResponse:
    """
    Render the index page of the dashboard.
    
    This view handles the request to the dashboard's main page and returns
    the rendered HTML template.
    """
    baby_date = BabyDate.objects.first()
    return render(request, 'dashboard/index.html', {'baby_date': baby_date})
