from django.db import models


class Job(models.Model):
    remotive_job_id = models.CharField(max_length=200, unique=True)  # 'id' from the response
    url = models.URLField()  # 'url' from the response
    title = models.CharField(max_length=500)  # 'title' from the response
    company_name = models.CharField(max_length=500)  # 'company_name' from the response
    company_logo = models.URLField(blank=True, null=True)  # 'company_logo' from the response
    category = models.CharField(max_length=500)  # 'category' from the response
    job_type = models.CharField(max_length=200)  # 'job_type' from the response
    publication_date = models.DateTimeField()  # 'publication_date' from the response
    candidate_required_location = models.CharField(max_length=500, blank=True,
                                                   null=True)  # 'candidate_required_location' from the response
    salary = models.CharField(max_length=200, blank=True, null=True)  # 'salary' from the response
    description = models.TextField(blank=True, null=True)  # 'description' from the response

    def __str__(self):
        return self.title


class JobTag(models.Model):
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='tags')
    tag = models.CharField(max_length=50)  # A tag from the 'tags' list in the response

    def __str__(self):
        return self.tag

class JobCategory(models.Model):
    remotive_id = models.IntegerField(unique=True)
    name = models.CharField(max_length=255)
    slug = models.CharField(max_length=255)

    def __str__(self):
        return self.name