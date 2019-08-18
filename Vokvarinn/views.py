# stjanidev

from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.shortcuts import render
from django.utils import timezone

from .forms import PlantForm, Waterform, ScheduleForm
from .models import Plants, PlantLog
from .tables import PlantTable, PlantLogTable
try:
    from djcelery.models import PeriodicTasks, PeriodicTask, IntervalSchedule
except:
    print ("djcelery import error....")
    pass
from django_tables2 import RequestConfig


def all_view(request, **kwargs):
    print ("all_view ...")
    table = Plants.objects.all().order_by('id')
    if kwargs:
        plant_id = (kwargs['pk'])
    #data = {'plant': plant,}
    waterform = Waterform()
    context = {
        'table' : table,
        'waterform' : waterform,
    }
    # table = Plants.objects.values_list('name', flat=True)
    return render(request, 'Vokvarinn/all_view.html', context)


def plant_detail_view(request, *argv, **kwargs):
    print("plant_detail_view request: ", request)
    for arg in argv:
        print("plant_detail_view arg passed: " + arg)
    for key, value in kwargs.items():
        print("plant_detail_view kwarg passed: key " + key + " value " + str(value))
    if kwargs:
        plant_id = (kwargs['pk'])
    else:
        print ("plant_detail_view plant id is 1 ! ")
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
        print ("plant_detail_view POST")
        instance = get_object_or_404(Plants, id=plant_id)
        form = Waterform(request.POST, instance=instance)
        print ("plant_detail_view FORM ", form)
        if form.is_valid():
            #form.save()
            plant_do_water(plant_id, form.cleaned_data.get('amount'))
            return render(request, "vokvarinn/plant_detail.html", context)
    return render(request, "vokvarinn/plant_detail.html", context)


def plants_list_all_view(request):
    print ("plants_list_all_view ...")
    planttable = PlantTable(Plants.objects.all())
    context = {
        'planttable': planttable,
    }
    return render(request, 'Vokvarinn/all_plants.html', context)


def plant_create_view(request):
    tasks = IntervalSchedule.objects.all()
    print ("plant_create_view tasks: ", tasks)
    if request.method == 'POST':
        form = PlantForm(request.POST, request.FILES)
        print("Inserting new plant: ", form['name'].value())
        if form.is_valid():
            form.save()
            # return render(request, 'Vokvarinn/plant_create')
            # handle_uploaded_file(request.FILES['file'])
            # print("Form error: ", form.errors)
            return redirect('all_view')
        else:
            print("Form error: ", form.errors)
            context = {'form': form,
                       'tasks': tasks}
            return render(request, 'Vokvarinn/plant_create.html', context)
    else:
        context = {'form': PlantForm,
                   'tasks': tasks}
        return render(request, 'Vokvarinn/plant_create.html', context)


def plant_do_water(plant_id, amount, *args, **kwargs):
    print ("plant_do_water name: {} amount: {}".format(plant_id, amount))
    if args:
        print ("plant_do_water args: ", args)
    if kwargs:
        print ("plant_do_water kwargs: ", kwargs)
    # takes id and creates log entry
    if kwargs:
        plant_id = (kwargs['pk'])
    if amount > 1:
        now_aware = timezone.now()
        Plants.objects.filter(id=plant_id).update(last_water=now_aware)
        log = PlantLog(last_water=now_aware, plant_id=plant_id, amount=amount)
        print("plant_do_water: ", log)
        print ("plant_do_water amount: ", amount)
        log.save(force_insert=True)

    return 0


def plant_water_view(request,  **kwargs):
    print ("plant_water_view ....")
    plant_id = str(kwargs['pk'])
#    plant_do_water(plant_id)
    water_log = PlantLogTable(PlantLog.objects.filter(plant_id=plant_id).order_by('-last_water'))
    #plantinfo = Plants.objects.get(pk=plant_id)
    plant = Plants.objects.get(id=plant_id)
    now_aware = timezone.now()
    time_since = now_aware - plant.last_water
    task_selected = IntervalSchedule.objects.get(pk=plant.water_schedule.id)
#    data = {'plant': plant, 'last_water': plant.last_water, 'info_url': plant.info_url, 'image': plant.image, 'water_schedule': task_selected, }
    data = {'plant': plant, 'last_water': plant.last_water, 'info_url': plant.info_url, 'image': plant.image,
            'water_schedule': task_selected, }
    water_form = Waterform(data=data)
    if request.method == 'POST':
        print ("water POST ", plant_id)
        #instance = get_object_or_404(Plants, plant=plant)
        instance = get_object_or_404(Plants, id=plant_id)
        form = Waterform(request.POST, request.FILES, instance=plant)

        if form.is_valid():
            print ("water form valid: ", form)
            plant_do_water(plant_id, form.cleaned_data.get('amount'))
            #form.save()
        else:
            print ("water form error: ", form)


    context = {
        'plant': plant,
        'time_since_water': time_since,
        'time_now': now_aware,
        'water_log': water_log,
        'water_form': water_form,
    }
    return render(request, 'Vokvarinn/plant_detail.html', context)


def plant_view_waterlog(request):
    print ("plant_view_waterlog ...")
    water_log = PlantLogTable(PlantLog.objects.filter().order_by('-last_water'))
    RequestConfig(request, paginate={'per_page': 25}).configure(water_log)
    context = {
        'waterlog': water_log,
    }
    return render(request, 'Vokvarinn/waterlog.html', context)

def plant_delete(self, **kwargs):
    print ("plant_delete ...")
    Plants.objects.get(id = kwargs['pk']).delete()
    return HttpResponseRedirect('/')

def plant_edit_view(request, **kwargs):
    print ("plant_edit_view .... ")
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
    print ("edit_schedule ....")
    form = ScheduleForm
    context = {

        'schedule': IntervalSchedule.objects.all(),
        'form': form,
    }
    if request.method == 'POST':
        #instance = get_object_or_404(IntervalSchedule, id=id)
        form = ScheduleForm(request.POST)#, instance=instance)
        # if form.is_valid():
        form.save()
        return HttpResponseRedirect('/')
    return render(request, 'Vokvarinn/edit_schedule.html', context)