from django.urls import path

from . import views


urlpatterns = [
    path('<int:shopping_list_id>/', views.shopping_list_detail, name='shopping_list_detail'),
    path('<int:shopping_list_id>/edit', views.shopping_list_edit, name='shopping_list_edit'),
    path('fetch/<int:shopping_list_id>/item-category/create/', views.fetch_add_item_category, name='fetch_add_item_category'),
    path('ajax/item-catrgory/create/', views.ajax_create_item_category, name='ajax_create_item_category'),
    path('ajax/item-category/change/', views.ajax_change_item_category, name='ajax_change_item_category'),
    path('ajax/item-category/status/change/', views.ajax_change_item_category_status, name='ajax_change_item_category_status'),
    path('ajax/item-category/name/change/', views.ajax_change_item_category_name, name='ajax_change_item_category_name'),
    path('ajax/item-record/create/', views.ajax_create_item_record, name='ajax_create_item_record'),
    path('ajax/item-record/change/', views.ajax_change_item_record, name='ajax_change_item_record'),
    path('ajax/item-record/name/change/', views.ajax_change_item_record_name, name='ajax_change_item_record_name'),
    path('ajax/item-record/quantity/change/', views.ajax_change_item_record_quantity, name='ajax_change_item_record_quantity'),
    path('ajax/item-record/note/change/', views.ajax_change_item_record_note, name='ajax_change_item_record_note'),
]