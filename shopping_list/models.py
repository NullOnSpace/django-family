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
        ('incomplete', '未完成'),
        ('complete', '已完成'),
        ('cancelled', '取消'),
        ('delayed', '推迟'),
    ]
    name = models.CharField("品类名", max_length=100)
    shopping_list = models.ForeignKey(
        ShoppingList, related_name='categories', on_delete=models.CASCADE)
    status = models.CharField(
        "状态", max_length=10, choices=STATUS_CHOICES, default='incomplete')
    note = models.TextField("备注", blank=True, null=True)

    class Meta:
        ordering = ['-status']

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


class ItemRecord(models.Model):
    name = models.CharField("单品名", max_length=100, blank=True, null=True)
    category = models.ForeignKey(
        ItemCategory, related_name='items', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField("数量", default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    note = models.TextField("备注", blank=True, null=True)

    def __str__(self):
        return f"{self.name} x {self.quantity} in {self.category.name}"
