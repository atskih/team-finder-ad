from http import HTTPStatus
from tempfile import TemporaryDirectory

from django.contrib.auth import get_user_model
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from .constants import PROJECTS_PER_PAGE
from .models import Project, Skill


class ProjectFlowTests(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp_media = TemporaryDirectory()
        cls.override = override_settings(MEDIA_ROOT=cls.temp_media.name)
        cls.override.enable()
        super().setUpClass()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        cls.override.disable()
        cls.temp_media.cleanup()

    @classmethod
    def setUpTestData(cls):
        user_model = get_user_model()
        cls.owner = user_model.objects.create_user(
            email="owner@example.com",
            password="password",
            name="Owner",
            surname="One",
        )
        cls.member = user_model.objects.create_user(
            email="member@example.com",
            password="password",
            name="Member",
            surname="Two",
        )
        cls.project = Project.objects.create(
            name="TeamFinder",
            description="Find teammates",
            owner=cls.owner,
        )
        cls.project.participants.add(cls.owner)

    def test_project_list_renders_projects(self):
        response = self.client.get(reverse("projects:list"))

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertContains(response, "TeamFinder")

    def test_create_project_adds_owner_as_participant(self):
        member_client = Client()
        member_client.force_login(self.member)

        response = member_client.post(
            reverse("projects:create"),
            {
                "name": "New idea",
                "description": "Build together",
                "github_url": "https://github.com/example/repo",
                "status": Project.STATUS_OPEN,
            },
        )

        project = Project.objects.get(name="New idea")
        self.assertRedirects(response, reverse("projects:details", kwargs={"project_id": project.id}))
        self.assertEqual(project.owner, self.member)
        self.assertIn(self.member, project.participants.all())

    def test_only_owner_can_complete_project(self):
        member_client = Client()
        member_client.force_login(self.member)
        forbidden = member_client.post(reverse("projects:complete", kwargs={"project_id": self.project.id}))

        owner_client = Client()
        owner_client.force_login(self.owner)
        allowed = owner_client.post(reverse("projects:complete", kwargs={"project_id": self.project.id}))
        self.project.refresh_from_db()

        self.assertEqual(forbidden.status_code, HTTPStatus.FORBIDDEN)
        self.assertJSONEqual(allowed.content, {"status": "ok", "project_status": "closed"})
        self.assertEqual(self.project.status, Project.STATUS_CLOSED)

    def test_owner_can_create_and_remove_project_skill(self):
        owner_client = Client()
        owner_client.force_login(self.owner)

        add_response = owner_client.post(
            reverse("projects:add_skill", kwargs={"project_id": self.project.id}),
            {"name": "Django"},
        )
        skill = Skill.objects.get(name="Django")
        remove_response = owner_client.post(
            reverse("projects:remove_skill", kwargs={"project_id": self.project.id, "skill_id": skill.id}),
        )

        self.assertEqual(add_response.status_code, HTTPStatus.OK)
        self.assertJSONEqual(
            add_response.content,
            {
                "id": skill.id,
                "name": "Django",
                "skill_id": skill.id,
                "created": True,
                "added": True,
            },
        )
        self.assertJSONEqual(remove_response.content, {"status": "ok", "removed": True})
        self.assertNotIn(skill, self.project.skills.all())

    def test_non_owner_cannot_manage_project_skills(self):
        member_client = Client()
        member_client.force_login(self.member)

        response = member_client.post(
            reverse("projects:add_skill", kwargs={"project_id": self.project.id}), {"name": "Python"}
        )

        self.assertEqual(response.status_code, HTTPStatus.FORBIDDEN)
        self.assertFalse(Skill.objects.filter(name="Python").exists())

    def test_project_list_filters_by_skill_name(self):
        django = Skill.objects.create(name="Django")
        other = Project.objects.create(name="Other", owner=self.member)
        self.project.skills.add(django)

        response = self.client.get(reverse("projects:list"), {"skill": "Django"})

        projects = list(response.context["projects"])
        self.assertEqual(projects, [self.project])
        self.assertNotIn(other, projects)

    def test_project_list_is_paginated_by_projects_per_page(self):
        projects_to_create = PROJECTS_PER_PAGE + 1 - Project.objects.count()
        for index in range(projects_to_create):
            Project.objects.create(name=f"Project {index}", owner=self.owner)

        response = self.client.get(reverse("projects:list"))

        self.assertEqual(len(response.context["projects"]), PROJECTS_PER_PAGE)
        self.assertTrue(response.context["page_obj"].has_next())
