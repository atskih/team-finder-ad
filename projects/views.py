from http import HTTPStatus

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_GET, require_POST

from team_finder.services import paginate_queryset

from .constants import PROJECTS_PER_PAGE, SKILL_SUGGESTIONS_LIMIT
from .forms import ProjectForm
from .models import Project, Skill
from .services import get_project_queryset, get_request_payload


def project_list(request):
    active_skill = request.GET.get("skill")
    projects = get_project_queryset()
    if active_skill:
        projects = projects.filter(skills__name=active_skill)

    page_obj = paginate_queryset(request, projects.distinct(), PROJECTS_PER_PAGE)
    context = {
        "projects": page_obj,
        "page_obj": page_obj,
        "all_skills": Skill.objects.order_by("name"),
        "active_skill": active_skill,
    }
    return render(request, "projects/project_list.html", context)


def project_details(request, project_id):
    project = get_object_or_404(
        get_project_queryset(),
        pk=project_id,
    )
    return render(request, "projects/project-details.html", {"project": project})


@login_required
def create_project(request):
    form = ProjectForm(request.POST or None)
    if form.is_valid():
        project = form.save(commit=False)
        project.owner = request.user
        project.save()
        project.participants.add(request.user)
        return redirect("projects:details", project_id=project.id)
    return render(request, "projects/create-project.html", {"form": form, "is_edit": False})


@login_required
def edit_project(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    if project.owner_id != request.user.id and not request.user.is_staff:
        return redirect("projects:details", project_id=project.id)

    form = ProjectForm(request.POST or None, instance=project)
    if form.is_valid():
        form.save()
        return redirect("projects:details", project_id=project.id)
    return render(request, "projects/create-project.html", {"form": form, "is_edit": True})


@login_required
@require_POST
def complete_project(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    if project.owner_id != request.user.id or project.status != Project.STATUS_OPEN:
        return JsonResponse({"status": "error"}, status=HTTPStatus.FORBIDDEN)

    project.status = Project.STATUS_CLOSED
    project.save(update_fields=["status"])
    return JsonResponse({"status": "ok", "project_status": Project.STATUS_CLOSED})


@login_required
@require_POST
def toggle_participate(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    participant = not project.participants.filter(pk=request.user.pk).exists()
    if participant:
        project.participants.add(request.user)
    else:
        project.participants.remove(request.user)
    return JsonResponse({"status": "ok", "participant": participant})


@require_GET
def skill_suggestions(request):
    query = request.GET.get("q", "").strip()
    skills = Skill.objects.filter(name__istartswith=query).order_by("name")[:SKILL_SUGGESTIONS_LIMIT]
    return JsonResponse(list(skills.values("id", "name")), safe=False)


@login_required
@require_POST
def add_skill(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    if project.owner_id != request.user.id:
        return JsonResponse({"status": "error"}, status=HTTPStatus.FORBIDDEN)

    payload = get_request_payload(request)
    skill_id = payload.get("skill_id")
    name = str(payload.get("name", "")).strip()
    created = False

    if skill_id:
        skill = get_object_or_404(Skill, pk=skill_id)
    elif name:
        skill, created = Skill.objects.get_or_create(name=name)
    else:
        return JsonResponse({"status": "error", "error": "skill_id or name is required"}, status=HTTPStatus.BAD_REQUEST)

    added = not project.skills.filter(pk=skill.pk).exists()
    if added:
        project.skills.add(skill)

    return JsonResponse(
        {
            "id": skill.id,
            "name": skill.name,
            "skill_id": skill.id,
            "created": created,
            "added": added,
        }
    )


@login_required
@require_POST
def remove_skill(request, project_id, skill_id):
    project = get_object_or_404(Project, pk=project_id)
    if project.owner_id != request.user.id:
        return JsonResponse({"status": "error"}, status=HTTPStatus.FORBIDDEN)

    skill = get_object_or_404(Skill, pk=skill_id)
    if not project.skills.filter(pk=skill.pk).exists():
        return JsonResponse({"status": "error"}, status=HTTPStatus.NOT_FOUND)

    project.skills.remove(skill)
    return JsonResponse({"status": "ok", "removed": True})
