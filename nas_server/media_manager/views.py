import io
import logging
import mimetypes
import os
import zipfile

from django.conf import settings
from django.db import transaction
from django.http import FileResponse, Http404, HttpResponse, StreamingHttpResponse
from django.utils import timezone
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.parsers import MultiPartParser
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from . import services
from .models import MediaFile, UploadHistory
from .serializers import MediaFileSerializer, UploadHistorySerializer

logger = logging.getLogger(__name__)


def get_user_from_request(request):
    """Auth via header token OR ?token= query param (required for <img src> tags)."""
    if request.user and request.user.is_authenticated:
        return request.user
    token_key = request.query_params.get("token")
    if token_key:
        try:
            return Token.objects.get(key=token_key).user
        except Token.DoesNotExist:
            pass
    return None


def safe_path(path: str) -> bool:
    """Return True only if path is inside NAS_STORAGE_ROOT (prevents path traversal)."""
    real = os.path.realpath(path)
    root = os.path.realpath(settings.NAS_STORAGE_ROOT)
    return real.startswith(root + os.sep) or real == root


class UploadView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser]

    def post(self, request):
        files = request.FILES.getlist("files")
        if not files:
            return Response({"error": "No files provided."}, status=status.HTTP_400_BAD_REQUEST)

        results = [self._handle_single(request.user, f) for f in files]
        return Response(results)

    def _handle_single(self, user, upload) -> dict:
        filename = os.path.basename(upload.name)

        if upload.size > settings.MAX_UPLOAD_SIZE_BYTES:
            logger.warning(f"Upload rejected — too large: {filename} ({upload.size} bytes)")
            return {"filename": filename, "status": "error",
                    "error": f"File exceeds {settings.MAX_UPLOAD_SIZE_MB} MB limit."}

        mime_type, _ = mimetypes.guess_type(filename)
        mime_type = mime_type or upload.content_type or "application/octet-stream"
        if mime_type not in settings.ALLOWED_MIME_TYPES:
            logger.warning(f"Upload rejected — disallowed type: {filename} ({mime_type})")
            UploadHistory.objects.create(
                user=user, filename=filename, success=False,
                error_message=f"File type not allowed: {mime_type}"
            )
            return {"filename": filename, "status": "error",
                    "error": f"File type '{mime_type}' is not allowed."}

        media_type = services.get_media_type(mime_type)

        file_hash = services.compute_hash(upload)
        if MediaFile.objects.filter(file_hash=file_hash).exists():
            logger.info(f"Duplicate upload skipped: {filename}")
            UploadHistory.objects.create(
                user=user, filename=filename, file_hash=file_hash,
                success=False, error_message="Duplicate file."
            )
            return {"filename": filename, "status": "duplicate"}

        dest_path = services.build_storage_path(user.id, filename, media_type)
        if not safe_path(dest_path):
            logger.error(f"Path traversal attempt blocked: {dest_path}")
            return {"filename": filename, "status": "error", "error": "Invalid file path."}

        try:
            file_size = services.save_file(upload, dest_path)
        except Exception as e:
            logger.error(f"Failed to save file {filename}: {e}")
            UploadHistory.objects.create(
                user=user, filename=filename, file_hash=file_hash,
                success=False, error_message=str(e)
            )
            return {"filename": filename, "status": "error", "error": "Failed to save file."}

        thumbnail_path = ""
        thumb_path = services.build_thumbnail_path(user.id, filename)
        if media_type == "image":
            if services.create_thumbnail(dest_path, thumb_path):
                thumbnail_path = thumb_path
        elif media_type == "video":
            if services.create_video_thumbnail(dest_path, thumb_path):
                thumbnail_path = thumb_path

        taken_at = None
        if media_type == "image":
            taken_at = services.extract_exif_date(dest_path)

        try:
            with transaction.atomic():
                media_file = MediaFile.objects.create(
                    user=user, filename=filename, file_path=dest_path,
                    thumbnail_path=thumbnail_path, file_hash=file_hash,
                    file_size=file_size, media_type=media_type,
                    mime_type=mime_type, taken_at=taken_at,
                    device_source=self.request.META.get("HTTP_USER_AGENT", "")[:255],
                )
                user.storage_used = (user.storage_used or 0) + file_size
                user.save(update_fields=["storage_used"])

            UploadHistory.objects.create(
                user=user, filename=filename, file_hash=file_hash, success=True
            )
            logger.info(f"Uploaded: {filename} ({file_size} bytes) for {user.username}")
            return {"filename": filename, "status": "uploaded", "id": media_file.pk}

        except Exception as e:
            logger.error(f"DB error saving {filename}: {e}")
            if os.path.exists(dest_path):
                os.remove(dest_path)
            return {"filename": filename, "status": "error", "error": "Database error."}


class MediaListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        page = max(1, int(request.query_params.get("page", 1)))
        page_size = min(max(1, int(request.query_params.get("page_size", 50))), 200)
        media_type = request.query_params.get("type")

        # Only show non-deleted items in the main gallery
        qs = MediaFile.objects.filter(user=request.user, is_deleted=False)
        if media_type in ("image", "video", "other"):
            qs = qs.filter(media_type=media_type)

        total = qs.count()
        start = (page - 1) * page_size
        items = qs[start: start + page_size]

        serializer = MediaFileSerializer(items, many=True, context={"request": request})
        return Response({"total": total, "page": page, "page_size": page_size,
                         "results": serializer.data})


class TrashListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        page = max(1, int(request.query_params.get("page", 1)))
        page_size = min(max(1, int(request.query_params.get("page_size", 50))), 200)

        qs = MediaFile.objects.filter(user=request.user, is_deleted=True)
        total = qs.count()
        start = (page - 1) * page_size
        items = qs[start: start + page_size]

        serializer = MediaFileSerializer(items, many=True, context={"request": request})
        return Response({"total": total, "page": page, "page_size": page_size,
                         "results": serializer.data})


class MediaDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        try:
            media = MediaFile.objects.get(pk=pk, user=request.user, is_deleted=False)
        except MediaFile.DoesNotExist:
            raise Http404
        return Response(MediaFileSerializer(media, context={"request": request}).data)

    def delete(self, request, pk):
        """Soft delete — moves to Trash."""
        try:
            media = MediaFile.objects.get(pk=pk, user=request.user, is_deleted=False)
        except MediaFile.DoesNotExist:
            raise Http404

        media.is_deleted = True
        media.deleted_at = timezone.now()
        media.save(update_fields=["is_deleted", "deleted_at"])

        logger.info(f"Soft-deleted media {pk} for {request.user.username}")
        return Response(status=status.HTTP_204_NO_CONTENT)


class RestoreView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        """Restore a trashed item back to the gallery."""
        try:
            media = MediaFile.objects.get(pk=pk, user=request.user, is_deleted=True)
        except MediaFile.DoesNotExist:
            raise Http404

        media.is_deleted = False
        media.deleted_at = None
        media.save(update_fields=["is_deleted", "deleted_at"])

        logger.info(f"Restored media {pk} for {request.user.username}")
        return Response(MediaFileSerializer(media, context={"request": request}).data)


class PermanentDeleteView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, pk):
        """Permanently remove file from disk and database."""
        try:
            media = MediaFile.objects.get(pk=pk, user=request.user, is_deleted=True)
        except MediaFile.DoesNotExist:
            raise Http404

        for path in [media.file_path, media.thumbnail_path]:
            if not path:
                continue
            if not safe_path(path):
                logger.error(f"Path traversal blocked on permanent delete: {path}")
                continue
            try:
                if os.path.exists(path):
                    os.remove(path)
            except OSError as e:
                logger.warning(f"Could not delete file {path}: {e}")

        with transaction.atomic():
            request.user.storage_used = max(0, (request.user.storage_used or 0) - media.file_size)
            request.user.save(update_fields=["storage_used"])
            media.delete()

        logger.info(f"Permanently deleted media {pk} for {request.user.username}")
        return Response(status=status.HTTP_204_NO_CONTENT)


class BatchDownloadView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        ids = request.data.get("ids", [])
        if not ids or not isinstance(ids, list):
            return Response({"error": "Provide a list of IDs."}, status=status.HTTP_400_BAD_REQUEST)

        media_files = MediaFile.objects.filter(
            pk__in=ids, user=request.user, is_deleted=False
        )

        buffer = io.BytesIO()
        with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as zf:
            for media in media_files:
                if safe_path(media.file_path) and os.path.exists(media.file_path):
                    zf.write(media.file_path, media.filename)

        buffer.seek(0)
        response = HttpResponse(buffer.read(), content_type="application/zip")
        response["Content-Disposition"] = 'attachment; filename="photos.zip"'
        return response


class ServeMediaView(APIView):
    """
    Serve a media file. Supports HTTP Range requests so browsers can
    seek within videos without downloading the whole file first.
    """
    permission_classes = [AllowAny]

    def get(self, request, pk):
        user = get_user_from_request(request)
        if not user:
            raise Http404

        try:
            media = MediaFile.objects.get(pk=pk, user=user)
        except MediaFile.DoesNotExist:
            raise Http404

        if not safe_path(media.file_path) or not os.path.exists(media.file_path):
            raise Http404

        file_path = media.file_path
        file_size = os.path.getsize(file_path)
        content_type = media.mime_type or "application/octet-stream"

        range_header = request.META.get("HTTP_RANGE", "").strip()
        if range_header.startswith("bytes="):
            # Parse "bytes=<start>-<end>"
            range_spec = range_header[6:]
            start_str, _, end_str = range_spec.partition("-")
            start = int(start_str) if start_str else 0
            end = int(end_str) if end_str else file_size - 1
            end = min(end, file_size - 1)
            length = end - start + 1

            def _stream():
                remaining = length
                with open(file_path, "rb") as f:
                    f.seek(start)
                    while remaining > 0:
                        chunk = f.read(min(65536, remaining))
                        if not chunk:
                            break
                        remaining -= len(chunk)
                        yield chunk

            response = StreamingHttpResponse(_stream(), status=206, content_type=content_type)
            response["Content-Range"] = f"bytes {start}-{end}/{file_size}"
            response["Accept-Ranges"] = "bytes"
            response["Content-Length"] = str(length)
            return response

        # Full file — still advertise range support so browser knows it can seek
        response = FileResponse(open(file_path, "rb"), content_type=content_type)
        response["Accept-Ranges"] = "bytes"
        response["Content-Length"] = str(file_size)
        return response


class ServeThumbnailView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, pk):
        user = get_user_from_request(request)
        if not user:
            raise Http404

        try:
            media = MediaFile.objects.get(pk=pk, user=user)
        except MediaFile.DoesNotExist:
            raise Http404

        if not media.thumbnail_path or not safe_path(media.thumbnail_path) \
                or not os.path.exists(media.thumbnail_path):
            raise Http404

        return FileResponse(open(media.thumbnail_path, "rb"), content_type="image/jpeg")


class UploadHistoryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        page_size = min(int(request.query_params.get("page_size", 50)), 100)
        history = UploadHistory.objects.filter(user=request.user)[:page_size]
        return Response(UploadHistorySerializer(history, many=True).data)