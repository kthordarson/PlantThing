from django.db import models
from django.utils import timezone
from imagekit.models import ImageSpecField
from imagekit.processors import Transpose
from djcelery.models import PeriodicTasks, PeriodicTask, IntervalSchedule

# Create your models here.
class BaseModel(models.Model):
    objects = models.Manager()


class Plants(BaseModel):
    name = models.CharField(max_length=120, verbose_name='Plant name')
    last_water = models.DateTimeField(default=timezone.now, blank=True, verbose_name='Last water')
    info_url = models.URLField(max_length=200, null=True, blank=True, verbose_name='Info url')
    water_schedule = models.ForeignKey(IntervalSchedule, on_delete=models.CASCADE, verbose_name='Watering schedule')
    #water_schedule = models.CharField(max_length=30, default="1")
    image = models.ImageField(null=True, blank=True, upload_to="static/plant_images/", verbose_name="Image")
    image_thumbnail = ImageSpecField(
        source='image',
        processors=[Transpose()],
        format='JPEG'
    )

    class Meta:
        ordering = ['name']
        verbose_name_plural = "Plants"

    def get_absolute_url(self):
        return '/plant/{0}/'.format(self.id)

    def __unicode__(self):
        return self.name

    def __str__(self):
        return self.name


class PlantLog(BaseModel):
    plant = models.ForeignKey(Plants, default=1, on_delete=models.SET_DEFAULT, verbose_name='Plant name')
    last_water = models.DateTimeField(default=timezone.now, verbose_name='Last water')
    amount = models.IntegerField(null=True, verbose_name='Amount')

    class Meta:
        verbose_name_plural = "Logs"

    def get_plant_link(self):
        return '/plant/{0}'.format(self.plant.id)
    @property
    def plantlog_id(self):
        return self.id

    def __unicode__(self):
        return str(self.id)

    def __str__(self):
        return str(self.plant)
