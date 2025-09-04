from django import forms
from django.utils import timezone

from .models import Feeding, BreastBumping, BodyTemperature, GrowthData, BabyDate


class BabyDateForm(forms.ModelForm):
    class Meta:
        model = BabyDate
        fields = ['nickname', 'last_menstrual_period',
                  'estimated_due_date', 'birthday', 'ultrasound_fixed_days']
        widgets = {
            'nickname': forms.TextInput(attrs={'class': 'form-control form-control-sm'}),
            'last_menstrual_period': forms.DateInput(attrs={'class': 'form-control form-control-sm', 'type': 'date'}),
            'estimated_due_date': forms.DateInput(attrs={'class': 'form-control form-control-sm', 'type': 'date'}),
            'birthday': forms.DateTimeInput(attrs={'class': 'form-control form-control-sm', 'type': 'datetime-local'}),
            'ultrasound_fixed_days': forms.NumberInput(attrs={'class': 'form-control form-control-sm', 'min': '0'}),
        }
        labels = {
            'nickname': '宝宝昵称',
            'last_menstrual_period': '最后一次月经',
            'estimated_due_date': '预产期',
            'birthday': '出生日期',
            'ultrasound_fixed_days': '超声修正天数',
        }


class FeedingForm(forms.ModelForm):
    class Meta:
        model = Feeding
        fields = ['baby_date', 'amount', 'note']
        widgets = {
            'baby_date': forms.HiddenInput(),
            'amount': forms.NumberInput(attrs={'class': 'form-control form-control-sm', 'min': '0'}),
            'note': forms.Textarea(attrs={'class': 'form-control form-control-sm', 'rows': 1}),
        }
        labels = {
            'amount': '喂养量 (ml)',
            'note': '备注',
        }


class FeedingWithTimeForm(forms.ModelForm):
    feed_at = forms.SplitDateTimeField(label="时间", widget=forms.SplitDateTimeWidget(
        date_attrs={'type': 'hidden'},
        time_attrs={'type': 'time', 'style': 'width:5rem;'},
    ))

    class Meta:
        model = Feeding
        fields = ['feed_at', 'baby_date', 'amount']
        widgets = {
            'baby_date': forms.HiddenInput(),
            'amount': forms.NumberInput(attrs={
                'class': 'form-control form-control-sm',
                'min': '0',
                'style': 'width:4rem;',
            }),
        }
        labels = {
            'feed_at': '时间',
            'amount': '喂养量 (ml)',
        }


class BreastBumpingForm(forms.ModelForm):
    class Meta:
        model = BreastBumping
        fields = ['amount', 'notes']
        widgets = {
            'amount': forms.NumberInput(attrs={'class': 'form-control form-control-sm', 'min': '0'}),
            'notes': forms.Textarea(attrs={'class': 'form-control form-control-sm', 'rows': 1}),
        }
        labels = {
            'amount': '收集量 (ml)',
            'notes': '备注',
        }


class BodyTemperatureForm(forms.ModelForm):
    class Meta:
        model = BodyTemperature
        fields = ['baby_date', 'temperature', 'measurement', 'notes']
        widgets = {
            'baby_date': forms.HiddenInput(),
            'temperature': forms.NumberInput(attrs={'class': 'form-control form-control-sm', 'min': '0'}),
            'measurement': forms.Select(attrs={'class': 'form-select form-control-sm'}),
            'notes': forms.Textarea(attrs={'class': 'form-control form-control-sm', 'rows': 1}),
        }
        labels = {
            'temperature': '体温 (°C)',
            'measurement': '测量方式',
            'notes': '备注',
        }


class GrowthDataForm(forms.ModelForm):
    class Meta:
        model = GrowthData
        fields = ['baby_date', 'weight', 'height', 'head_circumference']
        widgets = {
            'baby_date': forms.HiddenInput(),
            'weight': forms.NumberInput(attrs={'class': 'form-control form-control-sm', 'min': '0'}),
            'height': forms.NumberInput(attrs={'class': 'form-control form-control-sm', 'min': '0'}),
            'head_circumference': forms.NumberInput(attrs={'class': 'form-control form-control-sm', 'min': '0'}),
        }
        labels = {
            'weight': '体重 (kg)',
            'height': '身高 (cm)',
            'head_circumference': '头围 (cm)',
        }
