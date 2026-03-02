"""
Management command: regenerate thumbnails for all video files.

Usage:
    python manage.py regen_video_thumbs
"""
import os

from django.core.management.base import BaseCommand

from media_manager import services
from media_manager.models import MediaFile


class Command(BaseCommand):
    help = "Regenerate thumbnails for all video MediaFile records."

    def handle(self, *args, **options):
        videos = MediaFile.objects.filter(media_type="video", is_deleted=False)
        total = videos.count()
        self.stdout.write(f"Found {total} video(s) to process.\n")

        ok = 0
        for media in videos:
            if not media.file_path or not os.path.exists(media.file_path):
                self.stdout.write(f"  SKIP  {media.filename} — file missing on disk\n")
                continue

            thumb_path = services.build_thumbnail_path(media.user_id, media.filename)
            success = services.create_video_thumbnail(media.file_path, thumb_path)

            if success:
                media.thumbnail_path = thumb_path
                media.save(update_fields=["thumbnail_path"])
                self.stdout.write(f"  OK    {media.filename}\n")
                ok += 1
            else:
                self.stdout.write(f"  FAIL  {media.filename} — could not extract frame\n")

        self.stdout.write(f"\nDone: {ok}/{total} thumbnails regenerated.\n")
