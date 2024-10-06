from django.contrib import admin
from django_celery_beat.models import IntervalSchedule, PeriodicTask

from jobs.models import Job

# admin.site.register(PeriodicTask)
# admin.site.register(IntervalSchedule)

admin.site.register(Job)