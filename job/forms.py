from django import forms
from huggingface_hub import upload_folder


class ResumeUploadForm(forms.Form):
    resume = forms.FileField()
