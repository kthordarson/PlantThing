from django import forms
from flatpickr import DateTimePickerInput
from django.utils import timezone
from PIL import Image

from imagekit.forms import ProcessedImageField
from imagekit.processors import ResizeToFill, Transpose, ResizeToFit

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
    # image = forms.ImageField(required=False)
    image = ProcessedImageField(required=False, spec_id='Vokvarinn:image', processors=[Transpose()],
                                format='JPEG')

    class Meta:
        model = PlantLog
        fields = ['amount', 'image']


class PlantCreateForm(forms.ModelForm):
    name = forms.CharField(widget=forms.TextInput(attrs={'size': '40'}))
    last_water = forms.DateTimeField(widget=DateTimePickerInput(attrs={'size': '40'}), required=False)
    info_url = forms.URLInput()
    try:
        water_schedule = forms.Select(choices=list(IntervalSchedule.objects.values_list('id', 'every', 'period')))
    except Exception as e:
        print ('Error in form...{}'.format(e))
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
    plant = forms.ModelChoiceField(widget=forms.HiddenInput(), queryset=Plants.objects.all(), required=False)
    plant_id = forms.ModelChoiceField(widget=forms.HiddenInput(), queryset=Plants.objects.all(), required=False)
    # image = forms.ImageField(required=False, label='Select image')
    image = ProcessedImageField(spec_id='Vokvarinn:image', processors=[Transpose()], format='JPEG')

    class Meta:
        model = PlantImages
        fields = ['plant', 'image']
