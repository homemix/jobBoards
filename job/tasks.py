# tasks.py

import requests
from celery import shared_task
from .models import Job, JobTag  # Adjust the import according to your project structure


@shared_task
def fetch_and_save_jobs():
    # Fetch the job data from the API
    url = 'https://remotive.io/api/remote-jobs?limit=500'
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()

        # Iterate through the jobs in the JSON response
        for job_data in data['jobs']:  # 'jobs' is the key in the API response
            # Check if the job already exists (to avoid duplicates)
            job, created = Job.objects.get_or_create(
                remotive_job_id=job_data['id'],
                defaults={
                    'url': job_data['url'],
                    'title': job_data['title'],
                    'company_name': job_data['company_name'],
                    'company_logo': job_data['company_logo'],
                    'category': job_data['category'],
                    'job_type': job_data['job_type'],
                    'publication_date': job_data['publication_date'],
                    'candidate_required_location': job_data['candidate_required_location'],
                    'salary': job_data.get('salary', None),  # Salary may be optional
                    'description': job_data['description'],
                }
            )

            # If the job was created, also save its tags
            if created:
                for tag in job_data['tags']:  # 'tags' is a list in the response
                    JobTag.objects.create(job=job, tag=tag)

        print("Jobs have been saved successfully!")
    else:
        print("Failed to fetch data from Remotive API. Status code:", response.status_code)
