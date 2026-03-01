from django.conf import settings
from django.db import models


class MediaFile(models.Model):
    MEDIA_TYPES = [
        ("image", "Image"),
        ("video", "Video"),
        ("other", "Other"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="media_files",
    )
    filename = models.CharField(max_length=255)
    file_path = models.CharField(max_length=500)
    thumbnail_path = models.CharField(max_length=500, blank=True)
    file_hash = models.CharField(max_length=64, unique=True)  # SHA-256
    file_size = models.BigIntegerField()  # bytes
    media_type = models.CharField(max_length=10, choices=MEDIA_TYPES, default="image")
    mime_type = models.CharField(max_length=100, blank=True)
    taken_at = models.DateTimeField(null=True, blank=True)  # EXIF date
    uploaded_at = models.DateTimeField(auto_now_add=True)
    device_source = models.CharField(max_length=255, blank=True)

    # Soft-delete (Trash)
    is_deleted = models.BooleanField(default=False, db_index=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-uploaded_at"]

    def __str__(self):
        return f"{self.filename} ({self.user.username})"

    @property
    def url(self):
        return f"/api/media/{self.pk}/serve/"

    @property
    def thumbnail_url(self):
        if self.thumbnail_path:
            return f"/api/media/{self.pk}/thumbnail/"
        return None


class UploadHistory(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="upload_history",
    )
    filename = models.CharField(max_length=255)
    file_hash = models.CharField(max_length=64, blank=True)
    success = models.BooleanField(default=True)
    error_message = models.TextField(blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-uploaded_at"]

    def __str__(self):
        status = "✓" if self.success else "✗"
        return f"[{status}] {self.filename} — {self.user.username}"
