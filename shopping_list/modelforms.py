from django import forms
from .models import ItemCategory, ItemRecord


class ItemCategoryForm(forms.ModelForm):
    class Meta:
        model = ItemCategory
        fields = ['name', 'status', 'note']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control form-control-sm'}),
            'status': forms.Select(attrs={'class': 'form-select form-select-sm'}),
            'note': forms.Textarea(attrs={'class': 'form-control form-control-sm', 'rows': 2}),
        }

class ItemRecordForm(forms.ModelForm):
    class Meta:
        model = ItemRecord
        fields = ['name', 'quantity', 'note']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control form-control-sm'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control form-control-sm', 'min': 1}),
            'note': forms.Textarea(attrs={'class': 'form-control form-control-sm', 'rows': 2}),
        }