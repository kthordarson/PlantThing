# stjanidev

from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.shortcuts import render
from django.utils import timezone

from .forms import PlantCreateForm, Waterform, ScheduleForm, ImageForm
from .models import Plants, PlantLog, PlantImages
from .tables import PlantTable, PlantLogTable
from djcelery.models import PeriodicTasks, PeriodicTask, IntervalSchedule
from django_tables2 import RequestConfig
from .imagedata import ImageMetaData
import datetime
import os
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
    print("[plant_detail_view request] ", request)
    plant_id = (kwargs['pk'])
    plant = Plants.objects.get(id=plant_id)
    plant_images = PlantImages.objects.filter(plant=plant)
    print ('[plant_detail_view] images \n {}'.format(plant_images))
    now_aware = timezone.now()
    time_since = now_aware - plant.last_water
    try:
        imgdata = ImageMetaData(plant.image)
        imgexif = imgdata.get_exif_data()  # DateTimeDigitized
        imgdate = imgexif['DateTime']
    except:
        imgdate = datetime.datetime.now()
    print ("image date: ", imgdate)
    #datetime.datetime.strptime(datetime_str,,'%Y:%m:%d %H:%M:%S')
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
        'imgdate' : imgdate,
        'plant_images' : plant_images,
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

def insert_image(plant,image):
    # insert imange to database
    #image_to_insert = imageform.cleaned_data['image']
    print ("[insert_image] plant {}".format(plant))
    print ("[insert_image] image {}".format(image))
    #new_image = PlantImages(plant_id=plant.id, image=image)
    #Plants.objects.filter(id=plant.id).update(image=image)
    new_image = PlantImages(plant=plant,image=image)
    print ("[insert_image] new_image {} ".format(new_image))
    result = new_image.save(force_insert=True)
    print ("[insert_image] result {} ".format(result))
#newdoc = Document(docfile = request.FILES['docfile'])
#        Plants.objects.filter(id=plant_id).update(last_water=now_aware)
#        log = PlantLog(last_water=now_aware, plant_id=plant_id, amount=amount)

def add_new_image(request):
    # add image to db
    if request.method == 'POST':
        imageform = ImageForm(request.POST, request.FILES)
        print("[add_new_image]\n post {} \n files {} ".format(request.POST, request.FILES))
        if imageform.is_valid():
            new_image = imageform.save()
            print ("[add_new_image] imageform.save result: {} ".format(new_image))
            return redirect('all_view')
    context = {
        'imageform' : ImageForm
    }
    return render(request, 'Vokvarinn/add_image.html', context)


def add_new_image_manual(plant, postdata, filedata):
    # add image to db
    print("[add_new_image_manual] plant: {} \n POSTDATA {} \n FILEDATA {} ".format(plant, postdata, filedata))
    data = {'plant':plant, 'image':filedata}
    instance = get_object_or_404(Plants, id=plant.id)
    print ('[add_new_image_manual] INSTANCE: {} '.format(instance))
    imageform = ImageForm(data=data, instance=instance)
    if imageform.is_valid():
        new_image = imageform.save()
        print ("[add_new_image_manual] imageform.save result: {} ".format(new_image))

def view_all_images(request):
    # add image to db
    all_images = PlantImages.objects.all()
    print ('[all_images] {} '. format(all_images))
    context = {
        'all_images' : all_images
    }
    return render(request, 'Vokvarinn/view_all_images.html', context)

def create_new_plant_view(request):
    tasks = IntervalSchedule.objects.all()
    if request.method == 'POST':
        post_data = request.POST
        post_files = request.FILES
        plantform = PlantCreateForm(post_data)
        imageform = ImageForm(post_data, post_files)
        print("[create_new_plant] name: {} ". format(plantform['name'].value()))
        if plantform.is_valid():
            new_plant = plantform.save()
            plant = new_plant
            data = {'plant': plant, 'post_data':post_data, 'post_files':post_files}
            add_new_image_manual(plant, post_data, post_files)
            #imageform = ImageForm(data=data)
            #print('[create_new_plant] imageform result {}'.format(imageform))
            print('[create_new_plant] plantform.save result {}'.format(new_plant))
            #imageform['plant'] = new_plant
            #imageform.fields['plant'] = new_plant
            #if imageform.is_valid():
            #    new_image = imageform.save()
            #    print('[plant_create_view] imageform.save result {}'.format(new_image))
            #else:
            #    print("[plant_create_view] imageform invalid {}".format(imageform.errors))
            return redirect('all_view')
        else:
            print("[plant_create_view] plantform error: {}".format(plantform.errors))
            context = {'plantform': plantform,
                       'imageform': imageform,
                       'tasks': tasks}
            return render(request, 'Vokvarinn/plant_create.html', context)
    else:
        context = {'plantform': PlantCreateForm,
                   'imageform' : ImageForm,
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
    tasks = IntervalSchedule.objects.all()
    plant_id = str(kwargs['pk'])
    plant = Plants.objects.get(pk=plant_id)
    water_log = PlantLog.objects.filter(plant_id=plant_id)
    task_selected = IntervalSchedule.objects.get(pk=plant.water_schedule.id)
    data = {'name': plant.name, 'last_water': plant.last_water, 'info_url': plant.info_url, 'image': plant.image, 'water_schedule': task_selected, 'plant':plant,}

    # DEBUG
    print ("[ plant_edit_view ] data ",data)

    if request.method == 'POST':
        post_data = request.POST
        file_data = request.FILES
        instance = get_object_or_404(Plants, id=plant_id)
        plant = Plants.objects.get(pk=plant_id)
        # img_instance = get_object_or_404(Plants, plant=plant)
        plantform = PlantCreateForm(post_data, file_data, instance=instance)
        imageform = ImageForm(post_data, file_data, instance=instance)
        if imageform.is_valid():
            print ('[plant_edit_view] imageform valid {} '.format(imageform))
            imgedit = imageform.save()
            print ('[plant_edit_view] imageform saved: {} '.format(imgedit))
            #newdoc = Document(docfile = request.FILES['docfile'])
            #image_to_insert = PlantImages(plant=plant,image = file_data)
            #image_to_insert.save()
            #insert_image(plant, image_to_insert)
        else:
            print ("[ plant_edit_view ] imageform is INVALID error: {} ". format(imageform.errors))
        if plantform.is_valid():
            plant_edit = plantform.save()
            print ("[plant_edit_view] plantform saved {} ".format(plant_edit))
            return HttpResponseRedirect('/')
    else:
        plantform = PlantCreateForm(initial=data)
        imageform = ImageForm(initial=data)
    context = {
        'plants': plant,
        'plantform': plantform,
        'imageform' : imageform,
        'water_log': water_log,
    }

    return render(request, 'Vokvarinn/plant_edit.html', context)

def edit_schedule_view(request, **kwargs):
    print ("edit_schedule ....")
    form = ScheduleForm
    context = {

        'schedule': IntervalSchedule.objects.all(),
        'form': form,
    }
    if request.method == 'POST':
        #instance = get_object_or_404(IntervalSchedule, id=id)
        form = ScheduleForm(request.POST)#, instance=instance)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/')
    return render(request, 'Vokvarinn/edit_schedule.html', context)