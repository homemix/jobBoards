from celery import shared_task
from django.contrib import messages
from django.core.paginator import Paginator
from django.db import models
from django.shortcuts import render, redirect
from job.tasks import extract_resume_info

from django.shortcuts import get_object_or_404

import os
import textract

import spacy

nlp = spacy.load("en_core_web_sm")

from .forms import ResumeUploadForm

from django.contrib.auth.decorators import login_required
from django.core.files.storage import FileSystemStorage
from django.conf import settings
from django.shortcuts import render
from .models import Job, Resume, JobTag

try:
    nlp = spacy.load("en_core_web_sm")
    print("SpaCy model loaded successfully.")
except OSError as e:
    print(f"Error loading SpaCy model: {e}")


@login_required
def index(request):
    category_counts = Job.category_count()
    form = ResumeUploadForm()
    resume = Resume.objects.filter(user=request.user).last()
    if resume:

        if resume and resume.skills:
            # Split skills into individual skill keywords
            skills_list = [skill.strip() for skill in resume.skills.split(',') if skill]
        else:
            skills_list=[]

        # Build a Q object for skill matching using OR conditions for each skill
        skills_query = models.Q()
        for skill in skills_list:
            skills_query |= models.Q(description__icontains=skill)

        default_categories = ['general', 'misc']  # Example defaults
        categories = resume.categories if resume and resume.categories else ''
        category_list = [category.strip() for category in categories.split(',') if category] or default_categories

        # Now, filter the jobs based on the categories, skills, or summary
        matching_jobs = Job.objects.filter(
            models.Q(category__in=category_list )|  # Match by categories
            skills_query |  # Match any skill from the resume
            models.Q(description__icontains=resume.summary)  # Match by summary
        ).distinct()

        # Additional filtering by job tags (if job tags are associated with jobs)
        job_tags = JobTag.objects.filter(tag__in=resume.skills.split(',')).values_list('job', flat=True)
        tagged_jobs = Job.objects.filter(id__in=job_tags).distinct()

        # Combine both job lists
        all_matching_jobs = matching_jobs | tagged_jobs
        all_matching_jobs = all_matching_jobs.distinct()[:10]

        print(f'matching:{all_matching_jobs}')

        context = {
            'category_counts': category_counts,
            'matching_jobs': all_matching_jobs,
            'form': form,
        }
    else:
        context = {
            'category_counts': category_counts,
            'form': form,
        }

    return render(request, 'jobs/index.html', context)


def job_list(request):
    # Get the search query from the request
    search_query = request.GET.get('search', '').strip()

    # Start with all jobs
    all_jobs = Job.objects.all()

    # Filter by search query if it exists
    if search_query:
        all_jobs = all_jobs.filter(
            models.Q(title__icontains=search_query) |  # Match by job title
            models.Q(category__icontains=search_query) |  # Match by category
            models.Q(description__icontains=search_query) |  # Match by description
            models.Q(tags__tag__icontains=search_query)  # Match by job tag
        ).distinct()  # Ensure unique results

    # Get the total count of jobs after filtering
    total_jobs = all_jobs.count()
    paginator = Paginator(all_jobs, 10)  # Show 5 jobs per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'jobs': page_obj,
        'total_jobs': total_jobs,
        'search_query': search_query,  # Pass the search query to the template
    }
    return render(request, 'jobs/job_list.html', context)


@login_required
def upload_resume(request):
    if request.method == 'POST':
        form = ResumeUploadForm(request.POST, request.FILES)
        if form.is_valid():
            resume_file = request.FILES['resume']
            # Save the resume to a temporary location
            fs = FileSystemStorage()
            filename = fs.save(resume_file.name, resume_file)
            file_path = os.path.join(settings.MEDIA_ROOT, filename)

            # Extract text from the resume
            extracted_text = textract.process(file_path).decode('utf-8')

            # Use NLP techniques to extract job title, experience, skills, categories, and summary
            job_title, experience, skills, categories, summary = extract_resume_info(extracted_text)

            # Save the extracted data to the database (create or update)
            resume, created = Resume.objects.update_or_create(
                user=request.user,
                defaults={
                    'job_title': job_title,
                    'years_of_experience': experience,
                    'skills': skills,
                    'categories': ', '.join(categories),  # Assuming you have a field for categories
                    'summary': summary  # Assuming you have a field for summary
                }
            )

            # Optional: Print to check whether it was created or updated
            if created:
                print("New resume created.")
                messages.success(request, "Your resume is saved successfully")
            else:
                print("Existing resume updated.")
                messages.success(request, "Your resume updated successfully")
            # resume.save()

            return redirect('job_home')

            # return render(request, 'resume_uploaded.html', {'resume': resume})
    else:
        form = ResumeUploadForm()
        messages.error(request, 'Upload not working...')

        return redirect('job_home')
    # return render(request, 'jobs/index.html', {'form': form})


def job_detail(request, job_id):
    job = get_object_or_404(Job, id=job_id)
    return render(request, 'jobs/job_detail.html', {'job': job})
