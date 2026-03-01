import { Component, EventEmitter, Output } from '@angular/core';
import { timeout } from 'rxjs';
import { ApiService } from '../../core/api.service';

@Component({
  selector: 'app-upload',
  templateUrl: './upload.component.html',
  styleUrls: ['./upload.component.scss']
})
export class UploadComponent {
  @Output() uploaded = new EventEmitter<void>();

  dragging = false;
  uploading = false;
  results: { filename: string; status: string; error?: string }[] = [];

  private readonly MAX_FILE_SIZE_MB = 500;

  constructor(private api: ApiService) {}

  onDrop(event: DragEvent) {
    event.preventDefault();
    this.dragging = false;
    const files = Array.from(event.dataTransfer?.files || []);
    if (files.length) this.upload(files);
  }

  onFileSelect(event: Event) {
    const input = event.target as HTMLInputElement;
    const files = Array.from(input.files || []);
    if (files.length) this.upload(files);
  }

  upload(files: File[]) {
    // Client-side size check before upload
    const oversized = files.filter(f => f.size > this.MAX_FILE_SIZE_MB * 1024 * 1024);
    if (oversized.length) {
      this.results = oversized.map(f => ({
        filename: f.name,
        status: 'error',
        error: `Exceeds ${this.MAX_FILE_SIZE_MB} MB limit`
      }));
      return;
    }

    this.uploading = true;
    this.results = [];

    this.api.uploadFiles(files).pipe(
      timeout(300_000)  // 5 minute timeout
    ).subscribe({
      next: (res: any[]) => {
        this.results = res;
        this.uploading = false;
        if (res.some(r => r.status === 'uploaded')) {
          this.uploaded.emit();
        }
      },
      error: (err: any) => {
        const msg = err.name === 'TimeoutError'
          ? 'Upload timed out. Try smaller files.'
          : 'Upload failed. Check your connection.';
        this.results = [{ filename: 'Error', status: 'error', error: msg }];
        this.uploading = false;
      }
    });
  }
}
