import hashlib
import os
from datetime import datetime

from django.conf import settings


def compute_hash(file) -> str:
    """Compute SHA-256 hash of an uploaded file. Rewinds file after hashing."""
    sha256 = hashlib.sha256()
    file.seek(0)
    for chunk in iter(lambda: file.read(8192), b""):
        sha256.update(chunk)
    file.seek(0)
    return sha256.hexdigest()


def build_storage_path(user_id: int, filename: str) -> str:
    """
    Returns absolute storage path for a user's file.

    Structure:
        NAS_STORAGE/users/<user_id>/images/<YYYY>/<MM>/<DD>/<filename>
    """
    date_dir = datetime.now().strftime("%Y/%m/%d")
    rel = os.path.join("users", str(user_id), "images", date_dir, filename)
    return os.path.join(settings.NAS_STORAGE_ROOT, rel)


def build_thumbnail_path(user_id: int, filename: str) -> str:
    """Returns absolute path for a thumbnail file."""
    date_dir = datetime.now().strftime("%Y/%m/%d")
    thumb_name = f"thumb_{filename}"
    rel = os.path.join("users", str(user_id), "thumbnails", date_dir, thumb_name)
    return os.path.join(settings.NAS_STORAGE_ROOT, rel)


def save_file(upload, dest_path: str) -> int:
    """Write upload to dest_path. Returns bytes written."""
    os.makedirs(os.path.dirname(dest_path), exist_ok=True)
    size = 0
    upload.seek(0)
    with open(dest_path, "wb") as f:
        for chunk in upload.chunks():
            f.write(chunk)
            size += len(chunk)
    return size


def create_thumbnail(source_path: str, thumb_path: str, size=(400, 400)) -> bool:
    """Generate JPEG thumbnail. Returns True on success."""
    try:
        from PIL import Image

        os.makedirs(os.path.dirname(thumb_path), exist_ok=True)
        with Image.open(source_path) as img:
            img.thumbnail(size, Image.LANCZOS)
            if img.mode in ("RGBA", "P"):
                img = img.convert("RGB")
            img.save(thumb_path, "JPEG", quality=85)
        return True
    except Exception:
        return False


def extract_exif_date(source_path: str) -> datetime | None:
    """Extract DateTimeOriginal from EXIF, returns datetime or None."""
    try:
        from PIL import Image
        from PIL.ExifTags import TAGS

        with Image.open(source_path) as img:
            exif = img._getexif()
            if not exif:
                return None
            # Tag 36867 = DateTimeOriginal, 306 = DateTime
            date_str = exif.get(36867) or exif.get(306)
            if date_str:
                return datetime.strptime(date_str, "%Y:%m:%d %H:%M:%S")
    except Exception:
        pass
    return None


def get_media_type(mime_type: str) -> str:
    if mime_type.startswith("image/"):
        return "image"
    if mime_type.startswith("video/"):
        return "video"
    return "other"
