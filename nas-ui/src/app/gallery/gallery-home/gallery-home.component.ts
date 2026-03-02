import {
  AfterViewInit, Component, OnDestroy, OnInit
} from '@angular/core';
import { forkJoin } from 'rxjs';
import { ApiService } from '../../core/api.service';
import { AuthService } from '../../core/auth.service';
import { DateGroup, MediaFile } from '../../shared/models/media.model';

@Component({
  selector: 'app-gallery-home',
  templateUrl: './gallery-home.component.html',
  styleUrls: ['./gallery-home.component.scss']
})
export class GalleryHomeComponent implements OnInit, AfterViewInit, OnDestroy {
  groups: DateGroup[] = [];
  allPhotos: MediaFile[] = [];

  loading = false;
  page = 1;
  hasMore = true;

  showUpload = false;
  user: any = null;

  // Viewer
  viewerOpen = false;
  viewerIndex = 0;

  // Multi-select
  selectMode = false;
  selectedIds = new Set<number>();

  // Confirm dialog
  confirmMessage = '';
  confirmCallback: (() => void) | null = null;

  private observer: IntersectionObserver | null = null;

  constructor(private api: ApiService, private auth: AuthService) {}

  ngOnInit() {
    this.auth.user$.subscribe(u => this.user = u);
    this.loadPhotos();
  }

  ngAfterViewInit() {
    this.setupInfiniteScroll();
  }

  setupInfiniteScroll() {
    const sentinel = document.getElementById('scroll-sentinel');
    if (!sentinel) return;
    this.observer = new IntersectionObserver(entries => {
      if (entries[0].isIntersecting && !this.loading && this.hasMore) {
        this.loadPhotos();
      }
    }, { threshold: 0.1 });
    this.observer.observe(sentinel);
  }

  loadPhotos() {
    if (this.loading || !this.hasMore) return;
    this.loading = true;

    this.api.getMedia(this.page, 50).subscribe({
      next: (res: any) => {
        const newPhotos: MediaFile[] = res.results.map((p: any) => ({
          ...p,
          url: this.api.serveUrl(p.id),
          thumbnail_url: p.thumbnail_url ? this.api.thumbnailUrl(p.id) : null
        }));
        this.allPhotos = [...this.allPhotos, ...newPhotos];
        this.buildGroups();
        this.hasMore = this.allPhotos.length < res.total;
        this.page++;
        this.loading = false;
      },
      error: () => { this.loading = false; }
    });
  }

  buildGroups() {
    const map = new Map<string, { photos: MediaFile[]; sortKey: number }>();

    for (const photo of this.allPhotos) {
      const label = this.dateLabel(photo.taken_at || photo.uploaded_at);
      const sortKey = new Date(photo.taken_at || photo.uploaded_at).getTime();
      if (!map.has(label)) {
        map.set(label, { photos: [], sortKey });
      }
      map.get(label)!.photos.push(photo);
    }

    this.groups = Array.from(map.entries())
      .sort((a, b) => b[1].sortKey - a[1].sortKey)
      .map(([label, { photos }]) => ({ label, photos }));
  }

  dateLabel(dateStr: string): string {
    const date = new Date(dateStr);
    const now = new Date();
    const yesterday = new Date(now);
    yesterday.setDate(now.getDate() - 1);

    if (date.toDateString() === now.toDateString()) return 'Today';
    if (date.toDateString() === yesterday.toDateString()) return 'Yesterday';
    if (date.getFullYear() === now.getFullYear()) {
      return date.toLocaleDateString('en-US', { month: 'long', day: 'numeric' });
    }
    return date.toLocaleDateString('en-US', { month: 'long', year: 'numeric' });
  }

  // ── Viewer ──────────────────────────────────────────────────────────────────
  openPhoto(photo: MediaFile) {
    this.viewerIndex = this.allPhotos.findIndex(p => p.id === photo.id);
    this.viewerOpen = true;
  }

  onViewerClosed() {
    this.viewerOpen = false;
  }

  onViewerDeleted(id: number) {
    this.removePhoto(id);
    if (this.allPhotos.length === 0) this.viewerOpen = false;
    else {
      // Clamp viewerIndex if we just removed the last item
      this.viewerIndex = Math.min(this.viewerIndex, this.allPhotos.length - 1);
    }
  }

  // ── Multi-select ─────────────────────────────────────────────────────────────
  enterSelectMode() {
    this.selectMode = true;
  }

  onLongPress(photo: MediaFile) {
    this.selectMode = true;
    this.selectedIds = new Set([photo.id]);
  }

  toggleSelect(id: number) {
    const next = new Set(this.selectedIds);
    if (next.has(id)) next.delete(id);
    else next.add(id);
    this.selectedIds = next;
    if (this.selectedIds.size === 0) this.selectMode = false;
  }

  selectAll() {
    this.selectedIds = new Set(this.allPhotos.map(p => p.id));
  }

  onRangeSelect(ids: number[]) {
    const next = new Set(this.selectedIds);
    ids.forEach(id => next.add(id));
    this.selectedIds = next;
    this.selectMode = true;
  }

  clearSelection() {
    this.selectedIds = new Set();
    this.selectMode = false;
  }

  deleteSelected() {
    const count = this.selectedIds.size;
    this.confirmMessage = `Move ${count} photo${count > 1 ? 's' : ''} to Trash?`;
    this.confirmCallback = () => {
      const ids = Array.from(this.selectedIds);
      const calls = ids.map(id => this.api.deleteMedia(id));
      forkJoin(calls).subscribe(() => {
        ids.forEach(id => this.removePhoto(id));
        this.selectedIds = new Set();
        this.selectMode = false;
        this.confirmCallback = null;
      });
    };
  }

  downloadSelected() {
    this.api.batchDownload(Array.from(this.selectedIds));
  }

  // ── Upload ───────────────────────────────────────────────────────────────────
  onUploaded() {
    // Reset and reload from scratch so new photos appear
    this.allPhotos = [];
    this.groups = [];
    this.page = 1;
    this.hasMore = true;
    this.showUpload = false;
    this.loadPhotos();
  }

  // ── Helpers ──────────────────────────────────────────────────────────────────
  private removePhoto(id: number) {
    this.allPhotos = this.allPhotos.filter(p => p.id !== id);
    this.buildGroups();
  }

  onConfirm() { this.confirmCallback?.(); }
  onCancel() { this.confirmCallback = null; }

  logout() { this.auth.logout(); }

  ngOnDestroy() { this.observer?.disconnect(); }
}
