# Generated by Django 2.2.4 on 2019-08-21 14:29

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('djcelery', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='BaseModel',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
        ),
        migrations.CreateModel(
            name='PlantImages',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('plant_id', models.IntegerField(blank=True)),
                ('image', models.ImageField(blank=True, default='PlantImagesTEST.jpg', upload_to='static/plant_images/', verbose_name='Image')),
            ],
            options={
                'verbose_name_plural': 'Images',
            },
        ),
        migrations.CreateModel(
            name='Plants',
            fields=[
                ('basemodel_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='Vokvarinn.BaseModel')),
                ('name', models.CharField(max_length=120, verbose_name='Plant name')),
                ('last_water', models.DateTimeField(blank=True, default=django.utils.timezone.now, null=True, verbose_name='Last water')),
                ('info_url', models.URLField(blank=True, default='http://www.wikipedia.org', null=True, verbose_name='Info url')),
                ('image', models.ImageField(blank=True, default='DefaultPlant.jpg', null=True, upload_to='static/plant_images/', verbose_name='Image')),
                ('water_schedule', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='djcelery.IntervalSchedule', verbose_name='Watering schedule')),
            ],
            options={
                'verbose_name_plural': 'Plants',
                'ordering': ['name'],
            },
            bases=('Vokvarinn.basemodel',),
        ),
        migrations.CreateModel(
            name='PlantLog',
            fields=[
                ('basemodel_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='Vokvarinn.BaseModel')),
                ('last_water', models.DateTimeField(default=django.utils.timezone.now, verbose_name='Last water')),
                ('amount', models.IntegerField(default=100, null=True, verbose_name='Amount')),
                ('plant', models.ForeignKey(default=1, on_delete=django.db.models.deletion.SET_DEFAULT, to='Vokvarinn.Plants', verbose_name='Plant name')),
            ],
            options={
                'verbose_name_plural': 'Logs',
            },
            bases=('Vokvarinn.basemodel',),
        ),
    ]
