from django.contrib import admin
from .models import Plants, PlantLog, PlantImages


# Register your models here.
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
    fields = [('plant', 'image')]
    list_display = ('plant', 'image')

class MyModelAdmin(admin.ModelAdmin):
    def get_form(self, request, obj=None, **kwargs):
        form = super(MyModelAdmin, self).get_form(request, obj, **kwargs)
        form.base_fields['my_field_name'].initial = 'a'
        return form


admin.site.register(Plants, PlantsAdmin)
admin.site.register(PlantLog, PlantLogAdmin)
admin.site.register(PlantImages, PlantImageAdmin)
# admin.site.register(Plants, MyModelAdmin)
