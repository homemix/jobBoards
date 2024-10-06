# jobs/models.py
from django.db import models


class Job(models.Model):
    title = models.CharField(max_length=255)
    excerpt = models.TextField()
    company_name = models.CharField(max_length=255)
    company_logo = models.URLField(blank=True, null=True)
    employment_type = models.CharField(max_length=100)
    min_salary = models.IntegerField(blank=True, null=True)
    max_salary = models.IntegerField(blank=True, null=True)
    seniority = models.CharField(max_length=100)
    location_restrictions = models.CharField(max_length=255, blank=True, null=True)
    timezone_restrictions = models.CharField(max_length=255, blank=True, null=True)
    categories = models.CharField(max_length=255, blank=True, null=True)
    description = models.TextField()
    pub_date = models.DateTimeField()
    expiry_date = models.DateTimeField()
    application_link = models.URLField()
    guid = models.URLField(unique=True)

    def __str__(self):
        return self.title
