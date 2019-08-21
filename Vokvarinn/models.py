from django.db import models
from django.utils import timezone

try:
    from djcelery.models import PeriodicTasks, PeriodicTask, IntervalSchedule
except:
    pass


# from .tables import PlantLogTable

class BaseModel(models.Model):
    objects = models.Manager()


class Plants(BaseModel):
    name = models.CharField(max_length=120, verbose_name='Plant name')
    last_water = models.DateTimeField(default=timezone.now, verbose_name='Last water', editable=True, blank=True,
                                      null=True)
    info_url = models.URLField(max_length=200, null=True, blank=True, verbose_name='Info url',
                               default="http://www.wikipedia.org")
    water_schedule = models.ForeignKey(IntervalSchedule, on_delete=models.CASCADE, verbose_name='Watering schedule')
    # water_schedule = models.CharField(max_length=30, default="1")
    image = models.ImageField(null=True, blank=True, upload_to="static/plant_images/", verbose_name="Image",
                              default="DefaultPlant.jpg")

    class Meta:
        ordering = ['name']
        verbose_name_plural = "Plants"

    def get_waterings(self):
        water_log = PlantLog.objects.filter(plant_id=self.id).order_by('-last_water')[2:5]
        return water_log

    def get_absolute_url(self):
        return '/plant/{0}/'.format(self.id)

    def get_id(self):
        return self.id

    def __unicode__(self):
        return self.name

    def __str__(self):
        return self.name


class PlantLog(BaseModel):
    plant = models.ForeignKey(Plants, default=1, on_delete=models.SET_DEFAULT, verbose_name='Plant name')
    last_water = models.DateTimeField(default=timezone.now, verbose_name='Last water')
    amount = models.IntegerField(null=True, default=100, verbose_name='Amount')

    # image_id = models.IntegerField(blank=True, null=True, default=None, verbose_name="ImageID")
    # image = models.ImageField(null=True, verbose_name='PlantImage', blank=True, default=None)
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


class PlantImages(models.Model):
    # plant = models.ForeignKey(Plants, default=1, on_delete=models.CASCADE, verbose_name='Plant name')
    plant_id = models.IntegerField(blank=True)
    image = models.ImageField(blank=True, upload_to="static/plant_images/", verbose_name="Image",
                              default="PlantImagesTEST.jpg")

    class Meta:
        verbose_name_plural = 'Images'

    def get_id(self):
        return self.plant_id

    def __unicode__(self):
        return str(self.plant_id)

    def __str__(self):
        return str(self.plant_id)
