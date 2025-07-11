from django import forms
from .models import ItemCategory, ItemRecord


class ItemCategoryForm(forms.ModelForm):
    class Meta:
        model = ItemCategory
        fields = ['name', 'status', 'note']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control smart-submit'}),
            'status': forms.Select(attrs={'class': 'form-select smart-submit'}),
            'note': forms.Textarea(attrs={'class': 'form-control smart-submit', 'rows': 2}),
        }

class ItemRecordForm(forms.ModelForm):
    class Meta:
        model = ItemRecord
        fields = ['name', 'quantity', 'note']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control smart-submit'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control smart-submit', 'min': 1}),
            'note': forms.Textarea(attrs={'class': 'form-control smart-submit', 'rows': 2}),
        }