import itertools

import django_tables2 as tables
from django_tables2.utils import A

from .models import Plants, PlantLog


class PlantTable(tables.Table):
    # fav = ImageColumn()

    image = tables.TemplateColumn('<div class="crop"><img class="round-image" src="{{ record.image }}"></div> ')
    id = tables.LinkColumn('plant_detail', args=[A('pk')])
    name = tables.LinkColumn('plant_detail', args=[A('pk')])
    water_schedule = tables.LinkColumn('plant_detail', args=[A('pk')])
    last_water = tables.DateTimeColumn(format="d-m-Y H:i:s")
    waterings = PlantLog.objects.all()
    image = tables.TemplateColumn('<img width="300" height="300" src="{{ record.image_id }}"> ')

    class Meta:
        model = Plants
        fields = {'id'}
        template_name = 'django_tables2/bootstrap.html'


class PlantLogTable(tables.Table):
    #    last_water = tables.DateTimeColumn(format="d-m-Y H:i:s")
    plant = tables.Column()
    last_water = tables.Column()

    def __init__(self, *args, **kwargs):
        super(PlantLogTable, self).__init__(*args, **kwargs)
        self.counter = itertools.count()

    def render_row_number(self):
        return 'Row %d' % next(self.counter)

    def render_id(self, value):
        return '<%s>' % value

    class Meta:
        model = PlantLog
        fields = {'last_water', 'plant', 'amount'}
        sequence = ('last_water', 'plant', 'amount')
        template_name = 'django_tables2/bootstrap.html'
