from django.contrib import messages
from django.shortcuts import render, redirect

from job.models import Job

import os
import textract

import spacy

nlp = spacy.load("en_core_web_sm")

from .forms import ResumeUploadForm
from .models import Resume
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.core.files.storage import FileSystemStorage
from django.conf import settings

try:
    nlp = spacy.load("en_core_web_sm")
    print("SpaCy model loaded successfully.")
except OSError as e:
    print(f"Error loading SpaCy model: {e}")


def index(request):
    category_counts = Job.category_count()
    form = ResumeUploadForm()
    context = {
        'category_counts': category_counts,
        'form': form,
    }

    return render(request, 'jobs/index.html', context)


def job_list(request):
    return render(request, 'jobs/job_list.html')


def job_detail(request):
    return render(request, 'jobs/job_detail.html')


# nlp = spacy.load("en_core_web_sm")

def extract_resume_info(text):
    """
    Extract job title, experience, and skills from the resume text using NLP.
    """
    doc = nlp(text)
    job_title = None
    experience = None
    skills = []

    # Extract named entities for job titles and experience
    for ent in doc.ents:
        if ent.label_ == "ORG":
            job_title = ent.text  # Simplified, you can improve this
        if ent.label_ == "DATE":
            # This is a placeholder. Improve this logic based on your needs.
            experience = int(ent.text) if ent.text.isdigit() else 0

    # Example of finding skill keywords in the resume (you can improve with a skill dictionary)
    skill_keywords = ['Python', 'Django', 'Java', 'Machine Learning', 'Data Science']
    for token in doc:
        if token.text in skill_keywords:
            skills.append(token.text)

    return job_title, experience, ', '.join(skills)


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

            # Use NLP techniques to extract job titles, experience, and skills
            job_title, experience, skills = extract_resume_info(extracted_text)

            # Save the extracted data to the database
            resume = Resume.objects.create(
                user=request.user,
                job_title=job_title,
                years_of_experience=experience,
                skills=skills
            )
            resume.save()
            messages.success(request, "Your resume is saved successfully")
            return redirect('job_home')

            # return render(request, 'resume_uploaded.html', {'resume': resume})
    else:
        form = ResumeUploadForm()

    return redirect('job_home')
    # return render(request, 'jobs/index.html', {'form': form})


def get_matching_jobs(user_resume):
    """
    Find matching jobs based on the user's resume data.
    """
    jobs = Job.objects.filter(
        category__icontains=user_resume.job_title,  # Match job title or category
        description__icontains=user_resume.skills  # Match skills with job descriptions
    )
    return jobs


@login_required
def show_matching_jobs(request):
    user_resume = Resume.objects.get(user=request.user)
    matching_jobs = get_matching_jobs(user_resume)

    return render(request, 'jobs/matching_jobs.html', {'jobs': matching_jobs})
