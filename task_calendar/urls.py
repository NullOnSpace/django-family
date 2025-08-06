from django.urls import path

from . import views


urlpatterns = [
    path('fetch_change_task_status/', views.fetch_change_task_status, name='fetch_change_task_status'),
    path('fetch_delete_task/<int:task_id>', views.fetch_delete_task, name='fetch_delete_task'),
    path('create_task', views.create_task, name='create_task'),
]