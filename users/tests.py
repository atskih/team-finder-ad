from tempfile import TemporaryDirectory

from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings


class UserFlowTests(TestCase):
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
        self.user = user_model.objects.create_user(
            email="user@example.com",
            password="password",
            name="User",
            surname="Main",
        )
        self.other = user_model.objects.create_user(
            email="other@example.com",
            password="password",
            name="Other",
            surname="Person",
        )

    def test_register_creates_and_logs_in_user(self):
        response = self.client.post(
            "/users/register/",
            {
                "name": "Maria",
                "surname": "Ivanova",
                "email": "maria@example.com",
                "password": "password",
            },
        )

        self.assertRedirects(response, "/users/login/")
        self.assertTrue(get_user_model().objects.filter(email="maria@example.com").exists())

    def test_login_accepts_email_and_password(self):
        response = self.client.post(
            "/users/login/",
            {"email": "user@example.com", "password": "password"},
        )

        self.assertRedirects(response, "/projects/list/")

    def test_participants_list_shows_registered_users(self):
        response = self.client.get("/users/list/")

        participants = list(response.context["participants"])
        self.assertEqual(participants, [self.other, self.user])

    def test_profile_phone_normalization_and_uniqueness(self):
        self.client.force_login(self.user)

        response = self.client.post(
            "/users/edit-profile/",
            {
                "name": "User",
                "surname": "Main",
                "about": "",
                "phone": "89991234567",
                "github_url": "https://github.com/example",
            },
        )
        self.user.refresh_from_db()

        self.assertRedirects(response, f"/users/{self.user.id}/")
        self.assertEqual(self.user.phone, "+79991234567")
