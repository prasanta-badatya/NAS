import {
  Component, EventEmitter, HostListener, Input, OnDestroy, OnInit, Output
} from '@angular/core';
import { ApiService } from '../../core/api.service';
import { MediaFile } from '../../shared/models/media.model';

@Component({
  selector: 'app-viewer',
  templateUrl: './viewer.component.html',
  styleUrls: ['./viewer.component.scss']
})
export class ViewerComponent implements OnInit, OnDestroy {
  @Input() photos: MediaFile[] = [];
  @Input() startIndex = 0;
  @Output() closed = new EventEmitter<void>();
  @Output() deleted = new EventEmitter<number>();

  currentIndex = 0;
  showInfo = false;
  showConfirm = false;

  private touchStartX = 0;
  private touchStartY = 0;

  get current(): MediaFile { return this.photos[this.currentIndex]; }
  get hasPrev(): boolean { return this.currentIndex > 0; }
  get hasNext(): boolean { return this.currentIndex < this.photos.length - 1; }

  constructor(private api: ApiService) {}

  ngOnInit() {
    this.currentIndex = this.startIndex;
    document.body.style.overflow = 'hidden';
  }

  ngOnDestroy() {
    document.body.style.overflow = '';
  }

  @HostListener('document:keydown', ['$event'])
  onKeydown(e: KeyboardEvent) {
    if (e.key === 'ArrowRight') this.next();
    else if (e.key === 'ArrowLeft') this.prev();
    else if (e.key === 'Escape') this.close();
    else if (e.key === 'i') this.toggleInfo();
  }

  prev() { if (this.hasPrev) this.currentIndex--; }
  next() { if (this.hasNext) this.currentIndex++; }
  close() { this.closed.emit(); }
  toggleInfo() { this.showInfo = !this.showInfo; }

  onTouchStart(e: TouchEvent) {
    this.touchStartX = e.touches[0].clientX;
    this.touchStartY = e.touches[0].clientY;
  }

  onTouchEnd(e: TouchEvent) {
    const dx = this.touchStartX - e.changedTouches[0].clientX;
    const dy = this.touchStartY - e.changedTouches[0].clientY;
    // Only swipe horizontally if horizontal movement dominates
    if (Math.abs(dx) > Math.abs(dy) && Math.abs(dx) > 50) {
      if (dx > 0) this.next();
      else this.prev();
    }
  }

  download() {
    this.api.downloadMedia(this.current.id, this.current.filename);
  }

  confirmDelete() {
    this.showConfirm = true;
  }

  softDelete() {
    this.showConfirm = false;
    const id = this.current.id;
    this.api.deleteMedia(id).subscribe(() => {
      this.deleted.emit(id);
      // If there are no more photos, close the viewer
      if (this.photos.length <= 1) {
        this.close();
      } else {
        // Stay at same index (next photo slides in), but clamp to valid range
        if (this.currentIndex >= this.photos.length - 1) {
          this.currentIndex = this.photos.length - 2;
        }
      }
    });
  }

  formatSize(bytes: number): string {
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / 1024 / 1024).toFixed(1)} MB`;
  }

  formatDate(dateStr: string | null): string {
    if (!dateStr) return '—';
    return new Date(dateStr).toLocaleString('en-US', {
      year: 'numeric', month: 'long', day: 'numeric',
      hour: '2-digit', minute: '2-digit'
    });
  }
}