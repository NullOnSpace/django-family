from django.urls import path

from . import views


urlpatterns = [
    path('ajax/item-category/status/change/', views.ajax_change_item_category_status, name='ajax_change_item_category_status'),
]