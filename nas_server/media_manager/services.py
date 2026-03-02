import hashlib
import os
import subprocess
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


def build_storage_path(user_id: int, filename: str, media_type: str = "image") -> str:
    """
    Returns absolute storage path for a user's file.

    Structure:
        NAS_STORAGE/users/<user_id>/images/<YYYY>/<MM>/<DD>/<filename>
        NAS_STORAGE/users/<user_id>/videos/<YYYY>/<MM>/<DD>/<filename>
    """
    date_dir = datetime.now().strftime("%Y/%m/%d")
    subdir = "videos" if media_type == "video" else "images"
    rel = os.path.join("users", str(user_id), subdir, date_dir, filename)
    return os.path.join(settings.NAS_STORAGE_ROOT, rel)


def build_thumbnail_path(user_id: int, filename: str) -> str:
    """Returns absolute path for a JPEG thumbnail (always .jpg regardless of source ext)."""
    date_dir = datetime.now().strftime("%Y/%m/%d")
    base = os.path.splitext(filename)[0]
    thumb_name = f"thumb_{base}.jpg"
    rel = os.path.join("users", str(user_id), "thumbnails", date_dir, thumb_name)
    return os.path.join(settings.NAS_STORAGE_ROOT, rel)


def save_file(upload, dest_path: str) -> int:
    """Write upload to dest_path in chunks. Returns bytes written."""
    os.makedirs(os.path.dirname(dest_path), exist_ok=True)
    size = 0
    upload.seek(0)
    with open(dest_path, "wb") as f:
        for chunk in upload.chunks():
            f.write(chunk)
            size += len(chunk)
    return size


def create_thumbnail(source_path: str, thumb_path: str, size=(400, 400)) -> bool:
    """Generate JPEG thumbnail from an image. Returns True on success."""
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


def create_video_thumbnail(source_path: str, thumb_path: str, size=(400, 400)) -> bool:
    """
    Extract a representative frame from a video and save as JPEG thumbnail.

    Strategy:
      1. Try ffmpeg via subprocess (no Python dep, widely available).
      2. Fall back to opencv-python if ffmpeg is not on PATH.

    Returns True if a thumbnail was written successfully.
    """
    os.makedirs(os.path.dirname(thumb_path), exist_ok=True)

    # ── Attempt 1: ffmpeg ────────────────────────────────────────────────────
    try:
        result = subprocess.run(
            [
                "ffmpeg", "-y",
                "-ss", "00:00:03",          # seek 3 s in (avoids black opening frames)
                "-i", source_path,
                "-vframes", "1",
                "-vf", f"scale='min({size[0]},iw)':'min({size[1]},ih)':force_original_aspect_ratio=decrease",
                thumb_path,
            ],
            capture_output=True,
            timeout=60,
        )
        if result.returncode == 0 and os.path.exists(thumb_path):
            return True
    except (FileNotFoundError, subprocess.TimeoutExpired, Exception):
        pass

    # ── Attempt 2: opencv-python ─────────────────────────────────────────────
    try:
        import cv2
        from PIL import Image

        cap = cv2.VideoCapture(source_path)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        fps = cap.get(cv2.CAP_PROP_FPS) or 30
        # Target: 3 s in, but no more than 10 % into the video
        target_frame = min(int(fps * 3), max(0, int(total_frames * 0.1)))
        cap.set(cv2.CAP_PROP_POS_FRAMES, target_frame)
        ret, frame = cap.read()
        cap.release()

        if ret:
            img = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            img.thumbnail(size, Image.LANCZOS)
            img.save(thumb_path, "JPEG", quality=85)
            return True
    except Exception:
        pass

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
