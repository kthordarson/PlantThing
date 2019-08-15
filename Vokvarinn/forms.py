from django import forms
from flatpickr import DateTimePickerInput
from djcelery.models import IntervalSchedule
import json

from .models import Plants, PlantLog
TASK_CHOICES = [
    ('tassk1','krem1'),
    ('task2','krem2'),

]
#tasks = IntervalSchedule.objects.all().values()
#task_list = IntervalSchedule.objects.values_list('id', flat=True).distinct()


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
