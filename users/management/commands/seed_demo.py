from django.core.management.base import BaseCommand

from projects.models import Project, Skill
from users.models import User


class Command(BaseCommand):
    help = "Create demo users and projects for manual TeamFinder checks."

    def handle(self, *args, **options):
        users_data = [
            ("maria@yandex.ru", "password", "Мария", "Иванова"),
            ("alex@example.com", "password", "Алексей", "Петров"),
            ("olga@example.com", "password", "Ольга", "Смирнова"),
        ]

        users = []
        for email, password, name, surname in users_data:
            user, created = User.objects.get_or_create(
                email=email,
                defaults={"name": name, "surname": surname},
            )
            if created:
                user.set_password(password)
                user.save()
            users.append(user)

        python, django, design = [Skill.objects.get_or_create(name=name)[0] for name in ["Python", "Django", "UI/UX"]]

        for index, owner in enumerate(users, start=1):
            project, _ = Project.objects.get_or_create(
                owner=owner,
                name=f"Demo project {index}",
                defaults={
                    "description": "Тестовый проект для проверки TeamFinder.",
                    "github_url": "https://github.com/example/teamfinder",
                    "status": Project.STATUS_OPEN,
                },
            )
            project.participants.add(owner)
            if index == 1:
                project.skills.add(python, django)
            elif index == 2:
                project.skills.add(django)
            else:
                project.skills.add(design)

        self.stdout.write(self.style.SUCCESS("Demo data is ready."))
