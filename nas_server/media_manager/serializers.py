from rest_framework import serializers

from .models import MediaFile, UploadHistory


class MediaFileSerializer(serializers.ModelSerializer):
    url = serializers.SerializerMethodField()
    thumbnail_url = serializers.SerializerMethodField()

    class Meta:
        model = MediaFile
        fields = (
            "id",
            "filename",
            "file_size",
            "media_type",
            "mime_type",
            "taken_at",
            "uploaded_at",
            "device_source",
            "url",
            "thumbnail_url",
        )

    def get_url(self, obj):
        request = self.context.get("request")
        url = f"/api/media/{obj.pk}/serve/"
        return request.build_absolute_uri(url) if request else url

    def get_thumbnail_url(self, obj):
        if not obj.thumbnail_path:
            return None
        request = self.context.get("request")
        url = f"/api/media/{obj.pk}/thumbnail/"
        return request.build_absolute_uri(url) if request else url


class UploadHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = UploadHistory
        fields = ("id", "filename", "success", "error_message", "uploaded_at")
