from urllib.parse import urlparse

from django import forms

from .models import Project


class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ["name", "description", "github_url", "status"]
        labels = {
            "name": "Название проекта",
            "description": "Описание проекта",
            "github_url": "Ссылка на GitHub",
            "status": "Статус",
        }
        widgets = {
            "description": forms.Textarea(attrs={"rows": 5}),
        }

    def clean_github_url(self):
        github_url = self.cleaned_data.get("github_url", "").strip()
        if not github_url:
            return github_url
        host = urlparse(github_url).netloc.lower()
        if host not in {"github.com", "www.github.com"}:
            raise forms.ValidationError("Ссылка должна вести на GitHub")
        return github_url
