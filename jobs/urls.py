from django.urls import path

from jobs import views

urlpatterns = [
    path('', views.index, name='index'),
    path('job_list', views.job_list, name='job_list'),
]
