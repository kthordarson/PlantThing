from django import forms
from flatpickr import DateTimePickerInput
from django.utils import timezone

try:
    from djcelery.models import PeriodicTasks, PeriodicTask, IntervalSchedule
except:
    pass

from .models import Plants, PlantLog, PlantImages

PERIOD_CHOICES = (('days', 'Days'),
                  ('hours', 'Hours'),
                  ('minutes', 'Minutes'),
                  ('seconds', 'Seconds'),
                  ('microseconds', 'Microseconds'))


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
    image = forms.ImageField(required=False)

    class Meta:
        model = PlantLog
        fields = ['amount', 'image']


class PlantCreateForm(forms.ModelForm):
    name = forms.CharField()
    last_water = forms.DateTimeField(widget=DateTimePickerInput(), required=False)
    info_url = forms.URLInput()
    try:
        water_schedule = forms.Select(choices=list(IntervalSchedule.objects.values_list('id', 'every', 'period')))
    except:
        pass

    # image = forms.ImageField()
    class Meta:
        model = Plants
        fields = ['name', 'last_water', 'info_url', 'water_schedule']

    def __init__(self, *args, **kwargs):
        super(PlantCreateForm, self).__init__(*args, **kwargs)
        self.fields['last_water'].initial = timezone.now


class ImageForm(forms.ModelForm):
    # plant = forms.ModelChoiceField(widget=forms.HiddenInput(), queryset=Plants.objects.all())
    plant = forms.ModelChoiceField(widget=forms.HiddenInput(),queryset=Plants.objects.all(), required=False)
    image = forms.ImageField(required=False, label='Select image')

    class Meta:
        model = PlantImages
        fields = ['plant', 'image']
