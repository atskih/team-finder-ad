import json

from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_GET, require_POST

from .forms import ProjectForm
from .models import Project, Skill


def project_list(request):
    active_skill = request.GET.get("skill")
    projects = Project.objects.select_related("owner").prefetch_related("participants", "skills").all()
    if active_skill:
        projects = projects.filter(skills__name=active_skill)

    page_obj = Paginator(projects.distinct(), 12).get_page(request.GET.get("page"))
    context = {
        "projects": page_obj,
        "page_obj": page_obj,
        "all_skills": Skill.objects.order_by("name"),
        "active_skill": active_skill,
    }
    return render(request, "projects/project_list.html", context)


def project_details(request, project_id):
    project = get_object_or_404(
        Project.objects.select_related("owner").prefetch_related("participants", "skills"),
        pk=project_id,
    )
    return render(request, "projects/project-details.html", {"project": project})


@login_required(login_url="/users/login/")
def create_project(request):
    if request.method == "POST":
        form = ProjectForm(request.POST)
        if form.is_valid():
            project = form.save(commit=False)
            project.owner = request.user
            project.save()
            project.participants.add(request.user)
            return redirect(f"/projects/{project.id}/")
    else:
        form = ProjectForm()
    return render(request, "projects/create-project.html", {"form": form, "is_edit": False})


@login_required(login_url="/users/login/")
def edit_project(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    if project.owner_id != request.user.id and not request.user.is_staff:
        return redirect(f"/projects/{project.id}/")

    if request.method == "POST":
        form = ProjectForm(request.POST, instance=project)
        if form.is_valid():
            form.save()
            return redirect(f"/projects/{project.id}/")
    else:
        form = ProjectForm(instance=project)
    return render(request, "projects/create-project.html", {"form": form, "is_edit": True})


@login_required(login_url="/users/login/")
@require_POST
def complete_project(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    if project.owner_id != request.user.id or project.status != Project.STATUS_OPEN:
        return JsonResponse({"status": "error"}, status=403)

    project.status = Project.STATUS_CLOSED
    project.save(update_fields=["status"])
    return JsonResponse({"status": "ok", "project_status": Project.STATUS_CLOSED})


@login_required(login_url="/users/login/")
@require_POST
def toggle_participate(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    if project.participants.filter(pk=request.user.pk).exists():
        project.participants.remove(request.user)
        participant = False
    else:
        project.participants.add(request.user)
        participant = True
    return JsonResponse({"status": "ok", "participant": participant})


@require_GET
def skill_suggestions(request):
    query = request.GET.get("q", "").strip()
    skills = Skill.objects.filter(name__istartswith=query).order_by("name")[:10]
    return JsonResponse(list(skills.values("id", "name")), safe=False)


@login_required(login_url="/users/login/")
@require_POST
def add_skill(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    if project.owner_id != request.user.id:
        return JsonResponse({"status": "error"}, status=403)

    payload = _request_payload(request)
    skill_id = payload.get("skill_id")
    name = str(payload.get("name", "")).strip()
    created = False

    if skill_id:
        skill = get_object_or_404(Skill, pk=skill_id)
    elif name:
        skill, created = Skill.objects.get_or_create(name=name)
    else:
        return JsonResponse({"status": "error", "error": "skill_id or name is required"}, status=400)

    if project.skills.filter(pk=skill.pk).exists():
        added = False
    else:
        project.skills.add(skill)
        added = True

    return JsonResponse(
        {
            "id": skill.id,
            "name": skill.name,
            "skill_id": skill.id,
            "created": created,
            "added": added,
        }
    )


@login_required(login_url="/users/login/")
@require_POST
def remove_skill(request, project_id, skill_id):
    project = get_object_or_404(Project, pk=project_id)
    if project.owner_id != request.user.id:
        return JsonResponse({"status": "error"}, status=403)

    skill = get_object_or_404(Skill, pk=skill_id)
    if not project.skills.filter(pk=skill.pk).exists():
        return JsonResponse({"status": "error"}, status=404)

    project.skills.remove(skill)
    return JsonResponse({"status": "ok", "removed": True})


def _request_payload(request):
    if request.content_type == "application/json":
        try:
            return json.loads(request.body.decode("utf-8") or "{}")
        except json.JSONDecodeError:
            return {}
    return request.POST
