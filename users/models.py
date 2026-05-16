from io import BytesIO
from uuid import uuid4

from django.contrib.auth.models import (
    AbstractBaseUser,
    PermissionsMixin,
)
from django.core.files.base import ContentFile
from django.db import models
from django.utils import timezone
from PIL import Image, ImageDraw, ImageFont

from .constants import (
    AVATAR_BACKGROUND_COLOR,
    AVATAR_FONT_NAME,
    AVATAR_FONT_SIZE,
    AVATAR_FORMAT,
    AVATAR_IMAGE_SIZE,
    AVATAR_TEXT_ANCHOR,
    AVATAR_TEXT_COLOR,
    AVATAR_UPLOAD_PATH,
    AVATAR_VERTICAL_OFFSET,
    USER_ABOUT_MAX_LENGTH,
    USER_NAME_MAX_LENGTH,
    USER_PHONE_MAX_LENGTH,
)
from .managers import UserManager


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=USER_NAME_MAX_LENGTH)
    surname = models.CharField(max_length=USER_NAME_MAX_LENGTH)
    avatar = models.ImageField(upload_to=AVATAR_UPLOAD_PATH, blank=True)
    phone = models.CharField(max_length=USER_PHONE_MAX_LENGTH, blank=True)
    github_url = models.URLField(blank=True)
    about = models.TextField(max_length=USER_ABOUT_MAX_LENGTH, blank=True)
    date_joined = models.DateTimeField(default=timezone.now)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["name", "surname"]

    def __str__(self):
        return f"{self.name} {self.surname}".strip() or self.email

    def save(self, *args, **kwargs):
        if not self.avatar:
            self.avatar.save(self._avatar_filename(), self._generate_avatar(), save=False)
        super().save(*args, **kwargs)

    def _avatar_filename(self):
        return f"avatar_{uuid4()}.png"

    def _generate_avatar(self):
        initial = (self.name or self.email or "U")[0].upper()
        image_size = (AVATAR_IMAGE_SIZE, AVATAR_IMAGE_SIZE)
        image = Image.new("RGB", image_size, AVATAR_BACKGROUND_COLOR)
        draw = ImageDraw.Draw(image)

        try:
            font = ImageFont.truetype(AVATAR_FONT_NAME, AVATAR_FONT_SIZE)
        except OSError:
            font = ImageFont.load_default()

        bbox = draw.textbbox(AVATAR_TEXT_ANCHOR, initial, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        position = (
            (AVATAR_IMAGE_SIZE - text_width) / 2,
            (AVATAR_IMAGE_SIZE - text_height) / 2 - AVATAR_VERTICAL_OFFSET,
        )
        draw.text(position, initial, fill=AVATAR_TEXT_COLOR, font=font)

        buffer = BytesIO()
        image.save(buffer, format=AVATAR_FORMAT)
        return ContentFile(buffer.getvalue())
