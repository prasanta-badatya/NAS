import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
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

  // Auth
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

  // Media
  getMedia(page = 1, pageSize = 50): Observable<any> {
    return this.http.get(
      `${this.base}/media/?page=${page}&page_size=${pageSize}`,
      { headers: this.headers() }
    );
  }

  uploadFiles(files: File[]): Observable<any> {
    const form = new FormData();
    files.forEach(f => form.append('files', f));
    return this.http.post(`${this.base}/media/upload/`, form, { headers: this.headers() });
  }

  deleteMedia(id: number): Observable<any> {
    return this.http.delete(`${this.base}/media/${id}/`, { headers: this.headers() });
  }

  thumbnailUrl(id: number): string {
    const token = localStorage.getItem('token');
    return `${this.base}/media/${id}/thumbnail/?token=${token}`;
  }

  serveUrl(id: number): string {
    const token = localStorage.getItem('token');
    return `${this.base}/media/${id}/serve/?token=${token}`;
  }
}
