from django.db import models


class ShoppingList(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class ItemCategory(models.Model):
    STATUS_CHOICES = [
        ('incomplete', 'Incomplete'),
        ('complete', 'Complete'),
        ('cancelled', 'Cancelled'),
        ('delayed', 'Delayed'),
    ]
    name = models.CharField(max_length=100)
    shopping_list = models.ForeignKey(
        ShoppingList, related_name='categories', on_delete=models.CASCADE)
    status = models.CharField(
        max_length=10, choices=STATUS_CHOICES, default='incomplete')
    note = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.name} in {self.shopping_list.name}"

    def get_css_class(self):
        """Return a CSS class based on the status."""
        return {
            'incomplete': 'table-light',
            'complete': 'table-success',
            'cancelled': 'table-dark',
            'delayed': 'table-primary',
        }.get(self.status, 'table-primary')

class Item(models.Model):
    name = models.CharField(max_length=100)
    note = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name

class ItemRecord(models.Model):
    item = models.ForeignKey(
        Item, related_name='records', on_delete=models.CASCADE)
    category = models.ForeignKey(
        ItemCategory, related_name='items', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    note = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.item.name} x {self.quantity} in {self.category.name}"
