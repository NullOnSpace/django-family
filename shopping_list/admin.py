from django.contrib import admin

from .models import ShoppingList, ItemCategory, ItemRecord


admin.site.register(ShoppingList)
admin.site.register(ItemCategory)
admin.site.register(ItemRecord)