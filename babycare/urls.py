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
    path('create/', views.create_baby_date, name='create_baby_date'),
    path('feedings/<int:baby_date_id>/',
         views.feeding_list, name='feedings_list'),
    path('body_temperatures/<int:baby_date_id>',
         views.BodyTemperatureListView.as_view(),
         name='body_temperatures_list'),
    path('growth_datas/<int:baby_date_id>',
         views.GrowthDataListView.as_view(), name='growth_datas_list'),
    path('baby_date_relate_request/', views.baby_date_relate_request,
         name='baby_date_relate_request'),
    path('approve_baby_date_relate_request/',
         views.approve_baby_date_relate_request,
         name='approve_baby_date_relate_request'),
]
