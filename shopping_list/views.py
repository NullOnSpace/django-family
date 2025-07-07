import json

from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_POST

from .models import ShoppingList, ItemCategory


@require_POST
def ajax_change_item_category_status(request):
    res_json = json.loads(request.body)
    shopping_list_id = res_json.get('shopping_list_id')
    status = res_json.get('status')
    print(f"Received {res_json}")
    # Update the shopping list item status in the database
    try:
        item_category = ItemCategory.objects.get(id=shopping_list_id)
        item_category.status = status
        item_category.save()        
        return JsonResponse({
            'success': True, 
            'value': item_category.get_status_display(), # type: ignore
            'css_class': item_category.get_css_class()
        }) 
    except ShoppingList.DoesNotExist:
        return JsonResponse({'error': 'ItemCategory not found'})
