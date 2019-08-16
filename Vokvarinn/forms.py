from django import forms
from flatpickr import DateTimePickerInput
try:
    from djcelery.models import PeriodicTasks, PeriodicTask, IntervalSchedule
except:
    print ("djcelery import error....")
    pass

from .models import Plants, PlantLog

PERIOD_CHOICES = (('days', ('Days')),
                  ('hours', ('Hours')),
                  ('minutes', ('Minutes')),
                  ('seconds', ('Seconds')),
                  ('microseconds', ('Microseconds')))


class ScheduleForm(forms.ModelForm):
    every = forms.IntegerField()
    period = forms.ChoiceField(choices=PERIOD_CHOICES, required=True)

    class Meta:
        try:
            model = IntervalSchedule
        except:
            pass
        verbose_name = 'interval'
        verbose_name_plural = 'intervals'
        ordering = ['period', 'every']
        fields = ['every', 'period']

class Waterform(forms.ModelForm):
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
    try:
        water_schedule = forms.Select(choices=list(IntervalSchedule.objects.values_list('id', 'every', 'period')))
    except:
        pass
    image = forms.ImageField()
    class Meta:
        model = Plants
        fields = ['name', 'last_water', 'info_url', 'image', 'water_schedule']
