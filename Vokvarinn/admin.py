from django.contrib import admin
from .models import Plants, PlantLog, PlantImages


class PlantsAdmin(admin.ModelAdmin):
    fields = [
        ('name',
         'last_water',
         'water_schedule',
         'info_url',
         'image')
    ]

    search_fields = ['name']
    list_display = ('name', 'last_water', 'info_url', 'image', 'water_schedule')


class PlantLogAdmin(admin.ModelAdmin):
    fields = [('plant', 'last_water', 'amount')]
    list_display = ('plant', 'last_water', 'amount')


class PlantImageAdmin(admin.ModelAdmin):
    fields = [('plant_id', 'image')]
    list_display = ('plant_id', 'image')


admin.site.register(Plants, PlantsAdmin)
admin.site.register(PlantLog, PlantLogAdmin)
admin.site.register(PlantImages, PlantImageAdmin)
