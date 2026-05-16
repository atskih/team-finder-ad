import json
from pathlib import Path

from django.core.management.base import BaseCommand

from projects.models import Project, Skill
from users.models import User

DEMO_DATA_FILE = Path(__file__).with_name("demo_data.json")


class Command(BaseCommand):
    help = "Create demo users and projects for manual TeamFinder checks."

    def handle(self, *args, **options):
        demo_data = json.loads(DEMO_DATA_FILE.read_text(encoding="utf-8"))

        users_by_email = {}
        for user_data in demo_data["users"]:
            user, created = User.objects.get_or_create(
                email=user_data["email"],
                defaults={"name": user_data["name"], "surname": user_data["surname"]},
            )
            if created:
                user.set_password(user_data["password"])
                user.save()
            users_by_email[user.email] = user

        for project_data in demo_data["projects"]:
            owner = users_by_email[project_data["owner"]]
            project, _ = Project.objects.get_or_create(
                owner=owner,
                name=project_data["name"],
                defaults={
                    "description": project_data["description"],
                    "github_url": project_data["github_url"],
                    "status": Project.STATUS_OPEN,
                },
            )
            project.participants.add(owner)
            for skill_name in project_data["skills"]:
                skill, _ = Skill.objects.get_or_create(name=skill_name)
                project.skills.add(skill)

        self.stdout.write(self.style.SUCCESS("Demo data is ready."))
