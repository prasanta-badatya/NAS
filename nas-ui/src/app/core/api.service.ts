import { Injectable } from '@angular/core';
import {
  HttpClient, HttpHeaders, HttpRequest, HttpEvent
} from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment';

@Injectable({ providedIn: 'root' })
export class ApiService {
  private base = environment.apiUrl;

  constructor(private http: HttpClient) {}

  private headers(): HttpHeaders {
    const token = localStorage.getItem('token');
    return new HttpHeaders({ Authorization: `Token ${token}` });
  }

  // ── Auth ────────────────────────────────────────────────────────────────
  register(data: any): Observable<any> {
    return this.http.post(`${this.base}/auth/register/`, data);
  }

  login(data: any): Observable<any> {
    return this.http.post(`${this.base}/auth/login/`, data);
  }

  logout(): Observable<any> {
    return this.http.post(`${this.base}/auth/logout/`, {}, { headers: this.headers() });
  }

  profile(): Observable<any> {
    return this.http.get(`${this.base}/auth/profile/`, { headers: this.headers() });
  }

  // ── Gallery ─────────────────────────────────────────────────────────────
  getMedia(page = 1, pageSize = 50): Observable<any> {
    return this.http.get(
      `${this.base}/media/?page=${page}&page_size=${pageSize}`,
      { headers: this.headers() }
    );
  }

  // ── Trash ────────────────────────────────────────────────────────────────
  getTrash(page = 1, pageSize = 50): Observable<any> {
    return this.http.get(
      `${this.base}/media/trash/?page=${page}&page_size=${pageSize}`,
      { headers: this.headers() }
    );
  }

  restoreMedia(id: number): Observable<any> {
    return this.http.post(`${this.base}/media/${id}/restore/`, {}, { headers: this.headers() });
  }

  permanentDelete(id: number): Observable<any> {
    return this.http.delete(`${this.base}/media/${id}/permanent/`, { headers: this.headers() });
  }

  // ── Delete (soft) ────────────────────────────────────────────────────────
  deleteMedia(id: number): Observable<any> {
    return this.http.delete(`${this.base}/media/${id}/`, { headers: this.headers() });
  }

  // ── Upload with progress ─────────────────────────────────────────────────
  uploadFilesWithProgress(files: File[]): Observable<HttpEvent<any>> {
    const form = new FormData();
    files.forEach(f => form.append('files', f));
    const req = new HttpRequest('POST', `${this.base}/media/upload/`, form, {
      headers: this.headers(),
      reportProgress: true
    });
    return this.http.request(req);
  }

  // ── Download ─────────────────────────────────────────────────────────────
  downloadMedia(id: number, filename: string): void {
    this.http.get(`${this.base}/media/${id}/serve/`, {
      headers: this.headers(),
      responseType: 'blob'
    }).subscribe(blob => {
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = filename;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    });
  }

  batchDownload(ids: number[]): void {
    this.http.post(`${this.base}/media/batch-download/`, { ids }, {
      headers: this.headers(),
      responseType: 'blob'
    }).subscribe(blob => {
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = 'photos.zip';
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    });
  }

  // ── URL helpers (for <img src>) ──────────────────────────────────────────
  thumbnailUrl(id: number): string {
    const token = localStorage.getItem('token');
    return `${this.base}/media/${id}/thumbnail/?token=${token}`;
  }

  serveUrl(id: number): string {
    const token = localStorage.getItem('token');
    return `${this.base}/media/${id}/serve/?token=${token}`;
  }
}