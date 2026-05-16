from tempfile import TemporaryDirectory

from django.contrib.auth import get_user_model
from django.test import Client, TestCase, override_settings
from django.urls import reverse


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

    @classmethod
    def setUpTestData(cls):
        user_model = get_user_model()
        cls.user = user_model.objects.create_user(
            email="user@example.com",
            password="password",
            name="User",
            surname="Main",
        )
        cls.other = user_model.objects.create_user(
            email="other@example.com",
            password="password",
            name="Other",
            surname="Person",
        )

    def test_register_creates_and_logs_in_user(self):
        response = self.client.post(
            reverse("users:register"),
            {
                "name": "Maria",
                "surname": "Ivanova",
                "email": "maria@example.com",
                "password": "password",
            },
        )

        self.assertRedirects(response, reverse("users:login"))
        self.assertTrue(get_user_model().objects.filter(email="maria@example.com").exists())

    def test_login_accepts_email_and_password(self):
        response = self.client.post(
            reverse("users:login"),
            {"email": "user@example.com", "password": "password"},
        )

        self.assertRedirects(response, reverse("projects:list"))

    def test_participants_list_shows_registered_users(self):
        response = self.client.get(reverse("users:participants"))

        participants = list(response.context["participants"])
        self.assertEqual(participants, [self.other, self.user])

    def test_profile_phone_normalization_and_uniqueness(self):
        authenticated_client = Client()
        authenticated_client.force_login(self.user)

        response = authenticated_client.post(
            reverse("users:edit_profile"),
            {
                "name": "User",
                "surname": "Main",
                "about": "",
                "phone": "89991234567",
                "github_url": "https://github.com/example",
            },
        )
        self.user.refresh_from_db()

        self.assertRedirects(response, reverse("users:details", kwargs={"user_id": self.user.id}))
        self.assertEqual(self.user.phone, "+79991234567")
