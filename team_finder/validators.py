from urllib.parse import urlparse

from django import forms

GITHUB_HOSTS = {"github.com", "www.github.com"}


def validate_github_url(value):
    github_url = value.strip()
    if not github_url:
        return github_url

    host = urlparse(github_url).netloc.lower()
    if host not in GITHUB_HOSTS:
        raise forms.ValidationError("Ссылка должна вести на GitHub")
    return github_url
