import { Component, OnInit } from '@angular/core';
import { Router } from '@angular/router';
import { forkJoin } from 'rxjs';
import { ApiService } from '../../core/api.service';
import { MediaFile } from '../../shared/models/media.model';

@Component({
  selector: 'app-trash',
  templateUrl: './trash.component.html',
  styleUrls: ['./trash.component.scss']
})
export class TrashComponent implements OnInit {
  items: MediaFile[] = [];
  loading = true;

  confirmMessage = '';
  confirmCallback: (() => void) | null = null;

  constructor(private api: ApiService, private router: Router) {}

  ngOnInit() { this.load(); }

  load() {
    this.loading = true;
    this.api.getTrash().subscribe({
      next: (res: any) => {
        this.items = res.results.map((p: any) => ({
          ...p,
          url: this.api.serveUrl(p.id),
          thumbnail_url: p.thumbnail_url ? this.api.thumbnailUrl(p.id) : null
        }));
        this.loading = false;
      },
      error: () => { this.loading = false; }
    });
  }

  restore(id: number) {
    this.api.restoreMedia(id).subscribe(() => {
      this.items = this.items.filter(p => p.id !== id);
    });
  }

  promptPermanentDelete(id: number) {
    this.confirmMessage = 'Permanently delete this photo? This cannot be undone.';
    this.confirmCallback = () => {
      this.api.permanentDelete(id).subscribe(() => {
        this.items = this.items.filter(p => p.id !== id);
        this.confirmCallback = null;
      });
    };
  }

  promptEmptyTrash() {
    this.confirmMessage = `Permanently delete all ${this.items.length} items? This cannot be undone.`;
    this.confirmCallback = () => {
      const calls = this.items.map(item => this.api.permanentDelete(item.id));
      forkJoin(calls).subscribe(() => {
        this.items = [];
        this.confirmCallback = null;
      });
    };
  }

  onConfirm() {
    this.confirmCallback?.();
  }

  onCancel() {
    this.confirmCallback = null;
  }

  goBack() {
    this.router.navigate(['/gallery']);
  }

  formatSize(bytes: number): string {
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / 1024 / 1024).toFixed(1)} MB`;
  }
}
