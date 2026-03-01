import { Component, EventEmitter, Output } from '@angular/core';
import { HttpEvent, HttpEventType } from '@angular/common/http';
import { ApiService } from '../../core/api.service';

interface UploadItem {
  file: File;
  status: 'pending' | 'uploading' | 'done' | 'duplicate' | 'error';
  progress: number;
  error?: string;
}

@Component({
  selector: 'app-upload',
  templateUrl: './upload.component.html',
  styleUrls: ['./upload.component.scss']
})
export class UploadComponent {
  @Output() uploaded = new EventEmitter<void>();

  dragging = false;
  items: UploadItem[] = [];

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
    // Reset input so same file can be re-selected
    input.value = '';
  }

  upload(files: File[]) {
    this.items = files.map(file => {
      const oversize = file.size > this.MAX_FILE_SIZE_MB * 1024 * 1024;
      return {
        file,
        status: oversize ? 'error' : 'pending',
        progress: 0,
        error: oversize ? `Exceeds ${this.MAX_FILE_SIZE_MB} MB` : undefined
      } as UploadItem;
    });

    const valid = this.items.filter(i => i.status === 'pending');
    if (!valid.length) return;

    valid.forEach(item => {
      item.status = 'uploading';

      this.api.uploadFilesWithProgress([item.file]).subscribe({
        next: (event: HttpEvent<any>) => {
          if (event.type === HttpEventType.UploadProgress && event.total) {
            item.progress = Math.round(100 * event.loaded / event.total);
          } else if (event.type === HttpEventType.Response) {
            const result = event.body?.[0];
            item.progress = 100;
            item.status = result?.status === 'uploaded'  ? 'done'
                        : result?.status === 'duplicate' ? 'duplicate'
                        : 'error';
            item.error = result?.error;
            if (result?.status === 'uploaded') this.uploaded.emit();
          }
        },
        error: () => {
          item.status = 'error';
          item.error = 'Upload failed. Check your connection.';
        }
      });
    });
  }

  get statusIcon(): Record<string, string> {
    return { done: '✓', duplicate: '=', error: '✗', uploading: '…', pending: '·' };
  }
}
