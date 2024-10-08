# run_task.py

import os
import sys
import django

# Set the Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'jobBoards.settings')
# Setup Django
django.setup()

# Import the Celery task
from job.tasks import fetch_and_save_jobs, fetch_and_save_job_categories

# Call the task
if __name__ == "__main__":
    fetch_and_save_job_categories.delay()
    fetch_and_save_jobs.delay()  # Call the Celery task asynchronously
    print("Task has been queued.")
