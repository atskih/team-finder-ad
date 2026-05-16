import json

from .models import Project


def get_project_queryset():
    return Project.objects.select_related("owner").prefetch_related("participants", "skills")


def get_request_payload(request):
    if request.content_type == "application/json":
        try:
            return json.loads(request.body.decode("utf-8") or "{}")
        except json.JSONDecodeError:
            return {}
    return request.POST
