# tasks.py

import requests
from celery import shared_task
from django.conf import settings

from .models import Job, JobTag, JobCategory  # Adjust the import according to your project structure
import spacy
from celery import shared_task
import spacy
import re

nlp = spacy.load("en_core_web_sm")


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


API_URL = 'https://remotive.com/api/remote-jobs/categories'


@shared_task
def fetch_and_save_job_categories():
    # Fetch data from API
    response = requests.get(API_URL)

    if response.status_code == 200:
        data = response.json()

        # Iterate through the categories and save them to the database
        jobs = data.get('jobs', [])
        for job in jobs:
            category_id = job.get('id')
            name = job.get('name')
            slug = job.get('slug')

            # Create or update JobCategory in the database
            JobCategory.objects.update_or_create(
                remotive_id=category_id,
                defaults={'name': name, 'slug': slug}
            )
    else:
        print(f"Failed to fetch job categories. Status code: {response.status_code}")


# tasks.py

@shared_task
def extract_resume_info(text):
    """
    Extract job title, experience, skills, categories, and a summary from the resume text using NLP.
    """
    doc = nlp(text)
    job_title = None
    experience_years = 0  # Default experience if not found
    skills = []
    categories = []

    # Keywords and patterns for extraction
    job_title_keywords = ["ICT Officer", "Software Engineer", "Developer", "Data Scientist"]
    skill_keywords = [
        'Python', 'PHP', 'JavaScript', 'Power BI', 'Linear Regression',
        'Matplotlib', 'Sklearn', 'Machine Learning', 'HTML', 'CSS',
        'WordPress', 'SQL', 'PostgreSQL', 'MongoDB', 'Bootstrap',
        'Flask', 'FastAPI', 'Django', 'jQuery', 'Data Entry',
        'Data Analysis', 'Network Design', 'Configuration',
        'API Development', 'React', 'Ecommerce'
    ]
    category_keywords = ['Software Development', 'Data Science', 'Web Design', 'IT']

    # Extract job titles using keywords
    for token in doc:
        if token.text in job_title_keywords and not job_title:
            job_title = token.text  # Set job title if found

    # Extract years of experience by counting date-like patterns
    experience_pattern = r'(\d+)\s*(?:year|yr|years|month|mo|months)'
    matches = re.findall(experience_pattern, text, re.IGNORECASE)
    experience_years = sum(int(year) for year in matches)

    # Extract skills and categories using keyword matching
    for token in doc:
        if token.text in skill_keywords and token.text not in skills:
            skills.append(token.text)
        for category in category_keywords:
            if category.lower() in text.lower() and category not in categories:
                categories.append(category)

    # Summarize the resume text
    summary = summarize_resume(text)

    # Convert skills to a string format if needed
    skills = list(set(skills))  # Ensure skills are unique
    return job_title, experience_years, ', '.join(skills), categories, summary


def summarize_resume(text):
    """
    Summarize the resume text using the summarization pipeline.
    """

    import requests

    headers = {
        "Authorization": f"Bearer {settings.HUGGING_FACE_TOKEN}"
    }

    payload = {
        "inputs": text,
        "parameters": {
            "min_length": 200,  # Set your desired minimum length
            "max_length": 2000,  # Set your desired maximum length
            "do_sample": False  # Set to False for deterministic output
        }
    }

    response = requests.post(
        "https://api-inference.huggingface.co/models/facebook/bart-large-cnn",
        headers=headers,
        json=payload,
    )

    summary = response.json()
    # print(summary)
    return summary[0]['summary_text']
