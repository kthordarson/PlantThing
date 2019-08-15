from django import forms
from flatpickr import DateTimePickerInput
from djcelery.models import IntervalSchedule
from django.utils.translation import ugettext_lazy as _
import json

from .models import Plants, PlantLog

#tasks = IntervalSchedule.objects.all().values()
#task_list = IntervalSchedule.objects.values_list('id', flat=True).distinct()

PERIOD_CHOICES = (('days', ('Days')),
                  ('hours', ('Hours')),
                  ('minutes', ('Minutes')),
                  ('seconds', ('Seconds')),
                  ('microseconds', ('Microseconds')))


class ScheduleForm(forms.ModelForm):
    every = forms.IntegerField()
    period = forms.ChoiceField(choices=PERIOD_CHOICES, required=True)
    #period = forms.ModelChoiceField(queryset=IntervalSchedule.objects.all())
    #period = forms.CharField()
    
    
    class Meta:
        model = IntervalSchedule
        verbose_name = 'interval'
        verbose_name_plural = 'intervals'
        ordering = ['period', 'every']
        fields = ['every', 'period']

class DateTimeInput(forms.DateTimeInput):
    input_type = 'datetime'


class DateInput(forms.DateInput):
    input_type = 'date'

class Waterform(forms.ModelForm):
    #amount = forms.IntegerField()
    plant = forms.ModelChoiceField(widget=forms.HiddenInput(), queryset=Plants.objects.all())
    last_water = forms.DateTimeField(widget=forms.HiddenInput())
    amount = forms.IntegerField()
    class Meta:
        model  = PlantLog
        fields = ['amount']
class PlantForm(forms.ModelForm):
    name = forms.CharField()
    last_water = forms.DateTimeField(widget=DateTimePickerInput())
    info_url = forms.URLInput()
    water_schedule = forms.Select(choices=list(IntervalSchedule.objects.values_list('id', 'every', 'period')))
    image = forms.ImageField()
    class Meta:
        model = Plants
        fields = ['name', 'last_water', 'info_url', 'image', 'water_schedule']
