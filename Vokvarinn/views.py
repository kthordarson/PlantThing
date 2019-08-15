from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.shortcuts import render
from django.utils import timezone

from .forms import PlantForm, Waterform, ScheduleForm
from .models import Plants, PlantLog
from .tables import PlantTable, PlantLogTable
from djcelery.models import PeriodicTask, PeriodicTasks, IntervalSchedule
from datatableview.views import DatatableView
from django_tables2 import RequestConfig

#class ZeroConfigurationDatatableView(DatatableView):
#    model = Plants

class DatatableView(DatatableView):
    model = PlantLog
    datatable_options = {
        'columns': ['last_water','id',]
    }
    def get_context_data(self, **kwargs):
        context = super(DatatableView, self).get_context_data(**kwargs)
        context['last_water'] = self.model._meta.verbose_name_plural
        return context

def all_view(request):
    print("[ all_view ] IP Address for debug-toolbar: " + request.META['REMOTE_ADDR'])
    table = Plants.objects.all().order_by('id')
    # table = Plants.objects.values_list('name', flat=True)
    return render(request, 'Vokvarinn/all_view.html', {'table': table})


def plant_detail_view(request, *argv, **kwargs):
    print(request)
    for arg in argv:
        print("arg passed: " + arg)
    for key, value in kwargs.items():
        print("kwarg passed: key " + key + " value " + str(value))
    if kwargs:
        plant_id = (kwargs['pk'])
    else:
        plant_id = 1
    plant = Plants.objects.get(id=plant_id)
    now_aware = timezone.now()
    time_since = now_aware - plant.last_water
    task_selected = IntervalSchedule.objects.get(pk=plant.water_schedule.id)
    water_log = PlantLogTable(PlantLog.objects.filter(plant_id=plant_id).order_by('-last_water'))
    data = {'plant': plant, 'last_water': plant.last_water, 'info_url': plant.info_url, 'image': plant.image,
            'water_schedule': task_selected, }
    water_form = Waterform(data=data)

    context = {
        'plant': plant,
        'time_since_water': time_since,
        'time_now': now_aware,
        'water_log': water_log,
        'water_form': water_form,
    }

    if request.method == 'POST':
        print ("detail POST")
        instance = get_object_or_404(Plants, id=plant_id)
        form = Waterform(request.POST, instance=instance)
        print ("FORM ", form)
        if form.is_valid():
            #form.save()
            plant_do_water(plant_id, form.cleaned_data.get('amount'))
            return render(request, "vokvarinn/plant_detail.html", context)
    return render(request, "vokvarinn/plant_detail.html", context)


def plants_list_all_view(request):
    print("[ plant_list_all_view ]IP Address for debug-toolbar: " + request.META['REMOTE_ADDR'])
    # query = Plants.objects.all().order_by('id')
    # query = Plants.objects.order_by('id')
    # query = Plants.objects.values_list('name', flat=True)
    # query.extra(order_by = ['name'])
    planttable = PlantTable(Plants.objects.all())
    # planttable = PlantTable(Plants.objects.values_list('name', flat=True))
    # RequestConfig(request).configure(planttable)
    context = {
        'planttable': planttable,
    }
    return render(request, 'Vokvarinn/all_plants.html', context)


def plant_create_view(request):
    #    form = PlantForm(request.POST, request.FILES or None)
    # plant = Plants.objects.get(pk=1)
    # data = {'name':'plant.name', 'last_water':timezone.now(), 'info_url':'http://www.wikipedia.org', 'image':'',}
    tasks = IntervalSchedule.objects.all()
    print (tasks)
    if request.method == 'POST':
        form = PlantForm(request.POST, request.FILES)
        print("Inserting new plant: ", form['name'].value())
        if form.is_valid():
            form.save()
            # return render(request, 'Vokvarinn/plant_create')
            # handle_uploaded_file(request.FILES['file'])
            # print("Form error: ", form.errors)
            return redirect('plants_list_all_view')
        else:
            print("Form error: ", form.errors)
            context = {'form': form,
                       'tasks': tasks}
            return render(request, 'Vokvarinn/plant_create.html', context)
    else:
        context = {'form': PlantForm,
                   'tasks': tasks}
        return render(request, 'Vokvarinn/plant_create.html', context)


def plant_do_water(plant_id, amount):
    # takes id and creates log entry
    now_aware = timezone.now()
    Plants.objects.filter(id=plant_id).update(last_water=now_aware)
    log = PlantLog(last_water=now_aware, plant_id=plant_id, amount=amount)
    print("plant_do_water: ", log)
    log.save(force_insert=True)

    return 0


def plant_water_view(request,  **kwargs):
    plant_id = str(kwargs['pk'])
#    plant_do_water(plant_id)
    water_log = PlantLogTable(PlantLog.objects.filter(plant_id=plant_id).order_by('-last_water'))
    #plantinfo = Plants.objects.get(pk=plant_id)
    plant = Plants.objects.get(id=plant_id)
    now_aware = timezone.now()
    time_since = now_aware - plant.last_water
    task_selected = IntervalSchedule.objects.get(pk=plant.water_schedule.id)
    data = {'plant': plant, 'last_water': plant.last_water, 'info_url': plant.info_url, 'image': plant.image, 'water_schedule': task_selected, }
    if request.method == 'POST':
        print ("water POST")
        #instance = get_object_or_404(Plants, id=plant_id)
        form = Waterform(request.POST, data=data)
        if form.is_valid():
            print ("water form valid: ", form)
            form.save()

    context = {
        'plant': plant,
        'time_since_water': time_since,
        'time_now': now_aware,
        'water_log': water_log,
    }
    return render(request, 'Vokvarinn/plant_detail.html', context)


def plant_view_waterlog(request):
    # water_log = PlantLog.objects.all()
    water_log = PlantLogTable(PlantLog.objects.filter().order_by('-last_water'))
    RequestConfig(request, paginate={'per_page': 25}).configure(water_log)
    context = {
        'waterlog': water_log,
    }
    return render(request, 'Vokvarinn/waterlog.html', context)


def plant_edit_view(request, **kwargs):
    tasks = IntervalSchedule.objects.all()
    plant_id = str(kwargs['pk'])
    plant = Plants.objects.get(pk=plant_id)
    water_log = PlantLog.objects.filter(plant_id=plant_id)
    task_selected = IntervalSchedule.objects.get(pk=plant.water_schedule.id)
    print ("[ plant_edit_view ] tasks ", tasks)
    print ("[ plant_edit_view ] selected ", task_selected)
    data = {'name': plant.name, 'last_water': plant.last_water, 'info_url': plant.info_url, 'image': plant.image, 'water_schedule': task_selected, }
    print ("[ plant_edit_view ] ",data)
    if request.method == 'POST':
        instance = get_object_or_404(Plants, id=plant_id)
        form = PlantForm(request.POST, request.FILES, instance=instance)
        # if form.is_valid():
        form.save()
        return HttpResponseRedirect('/')
    else:
        form = PlantForm(initial=data)
    context = {
        'plants': plant,
        'form': form,
        'water_log': water_log,
    }

    return render(request, 'Vokvarinn/plant_edit.html', context)

def edit_schedule(request, **kwargs):
    form = ScheduleForm
    context = {

        'schedule': IntervalSchedule.objects.all(),
        'form': form,
    }
    return render(request, 'Vokvarinn/edit_schedule.html', context)