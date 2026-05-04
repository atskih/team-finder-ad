import re
from urllib.parse import urlparse

from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.forms import PasswordChangeForm

from .models import User


class RegisterForm(forms.ModelForm):
    password = forms.CharField(label="Пароль", widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ["name", "surname", "email", "password"]
        labels = {
            "name": "Имя",
            "surname": "Фамилия",
            "email": "Email",
        }

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user


class LoginForm(forms.Form):
    email = forms.EmailField(label="Email")
    password = forms.CharField(label="Пароль", widget=forms.PasswordInput)

    def __init__(self, request=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.request = request
        self.user = None

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get("email")
        password = cleaned_data.get("password")
        if email and password:
            self.user = authenticate(self.request, username=email, password=password)
            if self.user is None:
                raise forms.ValidationError("Неверный email или пароль")
        return cleaned_data


class ProfileForm(forms.ModelForm):
    avatar = forms.ImageField(
        label="Аватар",
        required=False,
        widget=forms.FileInput(
            attrs={
                "accept": "image/png,image/jpeg,image/webp,image/gif",
                "class": "visually-hidden",
            }
        ),
    )

    class Meta:
        model = User
        fields = ["name", "surname", "avatar", "about", "phone", "github_url"]
        labels = {
            "name": "Имя",
            "surname": "Фамилия",
            "avatar": "Аватар",
            "about": "О себе",
            "phone": "Телефон",
            "github_url": "Ссылка на GitHub",
        }

    def clean_phone(self):
        phone = self.cleaned_data.get("phone", "").strip()
        if not phone:
            return phone
        if not re.fullmatch(r"(8|\+7)\d{10}", phone):
            raise forms.ValidationError("Телефон должен быть в формате 8XXXXXXXXXX или +7XXXXXXXXXX")

        normalized = "+7" + phone[1:] if phone.startswith("8") else phone
        alternatives = [normalized, "8" + normalized[2:]]
        qs = User.objects.filter(phone__in=alternatives)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError("Пользователь с таким телефоном уже существует")
        return normalized

    def clean_github_url(self):
        github_url = self.cleaned_data.get("github_url", "").strip()
        if not github_url:
            return github_url
        host = urlparse(github_url).netloc.lower()
        if host not in {"github.com", "www.github.com"}:
            raise forms.ValidationError("Ссылка должна вести на GitHub")
        return github_url


class UserPasswordChangeForm(PasswordChangeForm):
    pass
