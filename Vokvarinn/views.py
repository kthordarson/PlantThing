# stjanidev
import datetime
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.shortcuts import render
from django.utils import timezone
from django_tables2 import RequestConfig
from djcelery.models import IntervalSchedule
from .forms import PlantCreateForm, Waterform, ScheduleForm, ImageForm
from .imagedata import ImageMetaData
from .models import Plants, PlantLog, PlantImages
from .tables import PlantTable, PlantLogTable
from PIL import Image, ExifTags

def all_view(request, **kwargs):
    table = Plants.objects.all().order_by('id')
    if kwargs:
        plant_id = (kwargs['pk'])
    waterform = Waterform()
    context = {
        'table': table,
        'waterform': waterform,
    }
    return render(request, 'Vokvarinn/all_view.html', context)


def plant_detail_view(request, *argv, **kwargs):
    print("[plant_detail_view request] ", request)
    plant_id = (kwargs['pk'])
    plant = Plants.objects.get(id=plant_id)
    plant_images = PlantImages.objects.filter(plant_id=plant_id)
    print('[plant_detail_view] images \n {}'.format(plant_images))
    now_aware = timezone.now()
    time_since = now_aware - plant.last_water
    try:
        imgdata = ImageMetaData(plant.image)
        imgexif = imgdata.get_exif_data()  # DateTimeDigitized
        imgdate = imgexif['DateTime']
    except:
        imgdate = datetime.datetime.now()
    print("image date: ", imgdate)
    # datetime.datetime.strptime(datetime_str,,'%Y:%m:%d %H:%M:%S')
    try:
        task_selected = IntervalSchedule.objects.get(pk=plant.water_schedule.id)
    except:
        task_selected = None
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
        'imgdate': imgdate,
        'plant_images': plant_images,
    }

    if request.method == 'POST':
        print("plant_detail_view POST")
        instance = get_object_or_404(Plants, id=plant_id)
        form = Waterform(request.POST, instance=instance)
        print("plant_detail_view FORM ", form)
        if form.is_valid():
            # form.save()
            plant_do_water(plant_id, form.cleaned_data.get('amount'))
            return render(request, "vokvarinn/plant_detail.html", context)
    return render(request, "vokvarinn/plant_detail.html", context)


def plants_list_all_view(request):
    planttable = PlantTable(Plants.objects.all())
    context = {
        'planttable': planttable,
    }
    return render(request, 'Vokvarinn/all_plants.html', context)


def insert_image(plant, image):
    # insert imange to database
    print("[insert_image] plant {}\n[insert_image] image {}".format(plant, image))
    new_image = PlantImages.object.create(plant=plant, image=image)
    result = new_image.save(force_insert=True)
    print("[insert_image] new_image {}\n[insert_image] result {} ".format(new_image, result))


def add_new_image(request, **kwargs):
    # add image to db
    if request.method == 'POST':
        plant_id = request.POST['plant_id'] or kwargs['pk']
        plant = Plants.objects.get(pk=plant_id)
        instance = get_object_or_404(Plants, id=plant_id)
        image_to_insert = request.FILES['image']
        data = {'plant': plant, 'plant_id': plant_id,  'image' : request.FILES['image'], }
        imageform = ImageForm(instance=instance, data=data)
        print("[add_new_image]\npost {}\nfiles {} ".format(request.POST, request.FILES))
        if imageform.is_valid():
            new_image = PlantImages(plant_id=plant_id, image=image_to_insert) #imageform.save(force_insert=True)
            new_image.save(force_insert=True)
            print("[add_new_image] imageform.save result: {} ".format(new_image))
            return redirect('view_all_images')
    context = {
        'imageform': ImageForm
    }
    return render(request, 'Vokvarinn/add_image.html', context)


def add_new_image_manual(plant, postdata, filedata):
    # add image to db
    print("[add_new_image_manual] plant: {} \n POSTDATA {} \n FILEDATA {} ".format(plant, postdata, filedata))
    data = {'plant': plant, 'image': filedata}
    instance = get_object_or_404(Plants, id=plant.id)
    imageform = ImageForm(data=data, instance=instance)
    if imageform.is_valid():
        new_image = imageform.save()


def view_all_images(request):
    # add image to db
    all_images = PlantImages.objects.all()
    print('[all_images] {} '.format(all_images))
    context = {
        'all_images': all_images
    }
    return render(request, 'Vokvarinn/view_all_images.html', context)


def create_new_plant_view(request):
    tasks = IntervalSchedule.objects.all()
    # todo if there is not IntervalSchedule, create one before creating new plant
    if request.method == 'POST':
        post_data = request.POST
        post_files = request.FILES
        image_to_insert = post_files['image']
        plantform = PlantCreateForm(post_data)
        imageform = ImageForm(post_data, post_files)
        print("[create_new_plant] name: {} ".format(plantform['name'].value()))
        if plantform.is_valid():
            new_plant = plantform.save()
            instance = get_object_or_404(Plants, id=new_plant.id)
            imageform = ImageForm(post_data, post_files, instance=instance)
            if imageform.is_valid():
                new_image = PlantImages(plant_id=new_plant.id, image=image_to_insert)  # imageform.save(force_insert=True)
                new_image.save(force_insert=True)
                imageform.save()
                # img_result = imageform.save()
                print('[create_new_plant] imgform.save result {}'.format(new_image))

            print('[create_new_plant] plantform.save result {}'.format(new_plant))
            return redirect('all_view')
        else:
            print("[plant_create_view] plantform error: {}".format(plantform.errors))
            context = {'plantform': plantform,
                       'imageform': imageform,
                       'tasks': tasks}
            return render(request, 'Vokvarinn/plant_create.html', context)
    else:
        context = {'plantform': PlantCreateForm,
                   'imageform': ImageForm,
                   'tasks': tasks}
        return render(request, 'Vokvarinn/plant_create.html', context)


def plant_edit_view(request, **kwargs):
    plant_id = str(kwargs['pk'])
    plant = Plants.objects.get(pk=plant_id)
    water_log = PlantLog.objects.filter(plant_id=plant_id)
    # task_selected = IntervalSchedule.objects.get(pk=plant.water_schedule.id) or None
    data = {'name': plant.name, 'last_water': plant.last_water, 'info_url': plant.info_url, 'image': plant.image,
             'plant': plant, }
    if request.method == 'POST':
        post_data = request.POST
        file_data = request.FILES
        instance = get_object_or_404(Plants, id=plant_id)
        plant = Plants.objects.get(pk=plant_id)
        # img_instance = get_object_or_404(Plants, plant=plant)
        plantform = PlantCreateForm(post_data, file_data, instance=instance)
        imageform = ImageForm(post_data, file_data, instance=instance)
        if imageform.is_valid():
            imgedit = imageform.save()
        else:
            print("[ plant_edit_view ] imageform is INVALID error: {} ".format(imageform.errors))
        if plantform.is_valid():
            plant_edit = plantform.save()
            return HttpResponseRedirect('/')
    else:
        plantform = PlantCreateForm(initial=data)
        imageform = ImageForm(initial=data)
    context = {
        'plants': plant,
        'plantform': plantform,
        'imageform': imageform,
        'water_log': water_log,
    }

    return render(request, 'Vokvarinn/plant_edit.html', context)


def plant_do_water(plant_id, amount, *args, **kwargs):
    # takes id and creates log entry
    #plant_id = kwargs['pk']
    if amount > 1:
        now_aware = timezone.now()
        Plants.objects.filter(id=plant_id).update(last_water=now_aware)
        log = PlantLog(last_water=now_aware, plant_id=plant_id, amount=amount)
        log.save(force_insert=True)
    return 0


def plant_water_view(request, **kwargs):
    plant_id = str(kwargs['pk'])
    #    plant_do_water(plant_id)
    water_log = PlantLogTable(PlantLog.objects.filter(plant_id=plant_id).order_by('-last_water'))
    # plantinfo = Plants.objects.get(pk=plant_id)
    plant = Plants.objects.get(id=plant_id)
    now_aware = timezone.now()
    time_since = now_aware - plant.last_water
    task_selected = IntervalSchedule.objects.get(pk=plant.water_schedule.id)
    #    data = {'plant': plant, 'last_water': plant.last_water, 'info_url': plant.info_url, 'image': plant.image, 'water_schedule': task_selected, }
    data = {'plant': plant, 'last_water': plant.last_water, 'info_url': plant.info_url, 'image': plant.image,
            'water_schedule': task_selected, }
    water_form = Waterform(data=data)
    if request.method == 'POST':
        print("water POST ", plant_id)
        # instance = get_object_or_404(Plants, plant=plant)
        instance = get_object_or_404(Plants, id=plant_id)
        form = Waterform(request.POST, request.FILES, instance=plant)

        if form.is_valid():
            print("water form valid: ", form)
            plant_do_water(plant_id, form.cleaned_data.get('amount'))
            # form.save()
        else:
            print("water form error: ", form)

    context = {
        'plant': plant,
        'time_since_water': time_since,
        'time_now': now_aware,
        'water_log': water_log,
        'water_form': water_form,
    }
    return render(request, 'Vokvarinn/plant_detail.html', context)


def plant_view_waterlog(request):
    water_log = PlantLogTable(PlantLog.objects.filter().order_by('-last_water'))
    RequestConfig(request, paginate={'per_page': 25}).configure(water_log)
    context = {
        'waterlog': water_log,
    }
    return render(request, 'Vokvarinn/waterlog.html', context)


def plant_delete(self, **kwargs):
    Plants.objects.get(id=kwargs['pk']).delete()
    return HttpResponseRedirect('/')


def edit_schedule_view(request, **kwargs):
    form = ScheduleForm
    context = {
        'schedule': IntervalSchedule.objects.all(),
        'form': form,
    }
    if request.method == 'POST':
        # instance = get_object_or_404(IntervalSchedule, id=id)
        form = ScheduleForm(request.POST)  # , instance=instance)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/')
    return render(request, 'Vokvarinn/edit_schedule.html', context)
