from django.urls import path

from . import views


urlpatterns = [
    path('fetch_change_task_status/', views.fetch_change_task_status, name='fetch_change_task_status'),
]