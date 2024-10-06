from django.shortcuts import render

from jobs.models import Job


# Create your views here.
def index(request):
    return render(request,'jobs/index.html')


def job_list(request):
    jobs = Job.objects.all()
    return render(request, 'jobs/job_list.html', {'jobs': jobs})
