from django.urls import path

from . import views

app_name = 'babycare'
urlpatterns = [
    # Define your URL patterns here
    path('fetch/submit_feeding/', views.fetch_submit_feeding,
         name='fetch_submit_feeding'),
    path('fetch/submit_breast_bumping/', views.fetch_submit_breast_bumping,
         name='fetch_submit_breast_bumping'),
    path('fetch/submit_body_temperature/', views.fetch_submit_body_temperature,
         name='fetch_submit_body_temperature'),
    path('fetch/submit_growth_data/', views.fetch_submit_growth_data,
         name='fetch_submit_growth_data'),

    path('', views.index, name='index'),
    path('feedings/', views.FeedingListView.as_view(), name='feedings_list'),
]
