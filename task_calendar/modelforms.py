from django import forms
from .models import TaskCalendar


class TaskCalendarForm(forms.ModelForm):
    class Meta:
        model = TaskCalendar
        fields = ['description', 'start_date', 'end_date', 'note']
        widgets = {
            'description': forms.TextInput(attrs={'class': 'form-control form-control-sm'}),
            'start_date': forms.DateInput(attrs={'class': 'form-control form-control-sm', 'type': 'date'}),
            'end_date': forms.DateInput(attrs={'class': 'form-control form-control-sm', 'type': 'date'}),
            'note': forms.Textarea(attrs={'class': 'form-control form-control-sm', 'rows': 2}),
        }