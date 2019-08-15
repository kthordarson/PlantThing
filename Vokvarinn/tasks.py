from logging import getLogger

from PlantThing.celery import app

from .models import Plants
from django.utils import timezone


@app.task
def check_water_task():
    # message = 'Checking water times....'
    # logger.debug('check water logger debug: ' + message)
    # print ('check water normal print: ' + message)
    table = Plants.objects.all()
    now_aware = timezone.now()

    for item in table:
        time_since = now_aware - item.last_water
        # print("time_since: ", time_since)
        # print ("time seconds: ", time_since.total_seconds())
        if time_since.total_seconds() > 120:  # 32000
            print("Checkwater item: {} time_since (seconds) {}".format(item, time_since.total_seconds()))
            # print ("time seconds: ", time_since.total_seconds())
