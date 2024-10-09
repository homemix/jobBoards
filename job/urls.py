from django.urls import path

from job import views

urlpatterns=[
    path('',views.index,name='job_home'),
    path('job_list/',views.job_list,name='job_list'),
    path('jobs/<int:job_id>/', views.job_detail, name='job_detail'),
    path('upload_resume/',views.upload_resume,name='upload_resume'),

]