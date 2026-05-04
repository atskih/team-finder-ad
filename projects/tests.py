from tempfile import TemporaryDirectory

from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings

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

    def setUp(self):
        user_model = get_user_model()
        self.owner = user_model.objects.create_user(
            email="owner@example.com",
            password="password",
            name="Owner",
            surname="One",
        )
        self.member = user_model.objects.create_user(
            email="member@example.com",
            password="password",
            name="Member",
            surname="Two",
        )
        self.project = Project.objects.create(
            name="TeamFinder",
            description="Find teammates",
            owner=self.owner,
        )
        self.project.participants.add(self.owner)

    def test_project_list_renders_projects(self):
        response = self.client.get("/projects/list/")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "TeamFinder")

    def test_create_project_adds_owner_as_participant(self):
        self.client.force_login(self.member)

        response = self.client.post(
            "/projects/create-project/",
            {
                "name": "New idea",
                "description": "Build together",
                "github_url": "https://github.com/example/repo",
                "status": Project.STATUS_OPEN,
            },
        )

        project = Project.objects.get(name="New idea")
        self.assertRedirects(response, f"/projects/{project.id}/")
        self.assertEqual(project.owner, self.member)
        self.assertIn(self.member, project.participants.all())

    def test_only_owner_can_complete_project(self):
        self.client.force_login(self.member)
        forbidden = self.client.post(f"/projects/{self.project.id}/complete/")

        self.client.force_login(self.owner)
        allowed = self.client.post(f"/projects/{self.project.id}/complete/")
        self.project.refresh_from_db()

        self.assertEqual(forbidden.status_code, 403)
        self.assertJSONEqual(allowed.content, {"status": "ok", "project_status": "closed"})
        self.assertEqual(self.project.status, Project.STATUS_CLOSED)

    def test_owner_can_create_and_remove_project_skill(self):
        self.client.force_login(self.owner)

        add_response = self.client.post(
            f"/projects/{self.project.id}/skills/add/",
            {"name": "Django"},
        )
        skill = Skill.objects.get(name="Django")
        remove_response = self.client.post(
            f"/projects/{self.project.id}/skills/{skill.id}/remove/",
        )

        self.assertEqual(add_response.status_code, 200)
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
        self.client.force_login(self.member)

        response = self.client.post(f"/projects/{self.project.id}/skills/add/", {"name": "Python"})

        self.assertEqual(response.status_code, 403)
        self.assertFalse(Skill.objects.filter(name="Python").exists())

    def test_project_list_filters_by_skill_name(self):
        django = Skill.objects.create(name="Django")
        other = Project.objects.create(name="Other", owner=self.member)
        self.project.skills.add(django)

        response = self.client.get("/projects/list/?skill=Django")

        projects = list(response.context["projects"])
        self.assertEqual(projects, [self.project])
        self.assertNotIn(other, projects)

    def test_project_list_is_paginated_by_12_items(self):
        for index in range(13):
            Project.objects.create(name=f"Project {index}", owner=self.owner)

        response = self.client.get("/projects/list/")

        self.assertEqual(len(response.context["projects"]), 12)
        self.assertTrue(response.context["page_obj"].has_next())
