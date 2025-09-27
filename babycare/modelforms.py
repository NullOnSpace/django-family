from django import forms
from django.utils import timezone

from . import models


class BabyDateForm(forms.ModelForm):
    class Meta:
        model = models.BabyDate
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
        model = models.Feeding
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
        model = models.Feeding
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
            'amount': '量 (ml)',
        }


class BreastBumpingForm(forms.ModelForm):
    class Meta:
        model = models.BreastBumping
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
        model = models.BodyTemperature
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
        model = models.GrowthData
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


class DiaperForm(forms.ModelForm):
    class Meta:
        model = models.Diaper
        fields = ['baby_date', 'pooh_amount', 'pooh_color',
                  'pee_amount', 'pee_color', 'notes']
        widgets = {
            'baby_date': forms.HiddenInput(),
            'pooh_amount': forms.Select(attrs={'class': 'form-select form-control-sm'}),
            'pooh_color': forms.Select(attrs={'class': 'form-select form-control-sm'}),
            'pee_amount': forms.Select(attrs={'class': 'form-select form-control-sm'}),
            'pee_color': forms.Select(attrs={'class': 'form-select form-control-sm'}),
            'notes': forms.Textarea(attrs={'class': 'form-control form-control-sm', 'rows': 1}),
        }
        labels = {
            'pooh_amount': '大便量',
            'pooh_color': '大便颜色',
            'pee_amount': '小便量',
            'pee_color': '小便颜色',
            'notes': '备注',
        }

    def clean(self):
        cd = super().clean()
        if cd.get('pooh_amount') == '0':
            cd['pooh_color'] = None
        if cd.get('pee_amount') == '0':
            cd['pee_color'] = None


class MiscRecordForm(forms.ModelForm):
    misc_item = forms.ModelChoiceField(
        label='营养剂/药剂名称',
        empty_label="请选择",
        queryset=models.MiscItem.objects,
        widget=forms.Select(attrs={'class': 'form-control  form-control-sm'})
    )

    class Meta:
        model = models.MiscRecord
        fields = ['baby_date', 'misc_item', 'notes']
        widgets = {
            'baby_date': forms.HiddenInput(),
            'notes': forms.Textarea(attrs={'class': 'form-control form-control-sm', 'rows': 1}),
        }
        labels = {
            'notes': '备注',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        baby_date = self['baby_date'].initial
        if baby_date:
            self.fields['misc_item'].queryset = models.MiscItem.objects.filter(baby_date=baby_date) # pyright: ignore[reportAttributeAccessIssue]
