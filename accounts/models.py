from django.db import models
from django.contrib.auth.models import AbstractUser
import uuid


class User(AbstractUser):
    pass


class RefreshToken(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="refresh_tokens",
    )

    token_hash = models.CharField(max_length=255, unique=True)

    family_id = models.UUIDField(default=uuid.uuid4, db_index=True)

    issued_at = models.DateTimeField(auto_now_add=True)

    expires_at = models.DateTimeField()

    revoked_at = models.DateTimeField(null=True, blank=True)

    replaced_by = models.OneToOneField(
        "self",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )

    def __str__(self):
        return f"{self.user.username} - {self.family_id}"

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(blank=True)
    location = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return self.user.username