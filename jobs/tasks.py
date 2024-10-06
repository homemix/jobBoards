import requests
from celery import shared_task

from .models import Job


@shared_task
def test_task():
    print(f'my tasks are running......')


@shared_task
def fetch_jobs_from_api():
    url = "https://himalayas.app/jobs/api?limit=100&offset=10"
    response = requests.get(url)
    print(f'status: {response.status_code}')
    print(response)

    if response.status_code == 200:
        jobs_data = response.json().get('jobs', [])

        for job in jobs_data:
            Job.objects.update_or_create(
                title=job.get('title'),
                defaults={
                    'excerpt': job.get('excerpt'),
                    'company_name': job.get('companyName'),
                    'company_logo': job.get('companyLogo'),
                    'employment_type': job.get('employmentType'),
                    'min_salary': job.get('minSalary'),
                    'max_salary': job.get('maxSalary'),
                    'seniority': job.get('seniority', [])[0] if job.get('seniority') else None,
                    'location_restrictions': ', '.join(job.get('locationRestrictions', [])),
                    'timezone_restrictions': ', '.join(map(str, job.get('timezoneRestrictions', []))),
                    'categories': ', '.join(job.get('categories', [])),
                    'description': job.get('description'),
                    'pub_date': job.get('pubDate'),
                    'expiry_date': job.get('expiryDate'),
                    'application_link': job.get('applicationLink'),
                    'guid': job.get('guid')
                }
            )
    else:
        print("Failed to fetch jobs: Status Code", response.status_code)
