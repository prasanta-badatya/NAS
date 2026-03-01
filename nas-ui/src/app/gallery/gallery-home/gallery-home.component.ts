import { Component, OnInit } from '@angular/core';
import { ApiService } from '../../core/api.service';
import { AuthService } from '../../core/auth.service';

@Component({
  selector: 'app-gallery-home',
  templateUrl: './gallery-home.component.html',
  styleUrls: ['./gallery-home.component.scss']
})
export class GalleryHomeComponent implements OnInit {
  photos: any[] = [];
  loading = true;
  showUpload = false;
  user: any = null;

  constructor(private api: ApiService, private auth: AuthService) {}

  ngOnInit() {
    this.auth.user$.subscribe(u => this.user = u);
    this.loadPhotos();
  }

  loadPhotos() {
    this.loading = true;
    this.api.getMedia().subscribe({
      next: (res: any) => {
        this.photos = res.results.map((p: any) => ({
          ...p,
          url: this.api.serveUrl(p.id),
          thumbnail_url: p.thumbnail_url ? this.api.thumbnailUrl(p.id) : null
        }));
        this.loading = false;
      },
      error: () => { this.loading = false; }
    });
  }

  onUploaded() {
    this.showUpload = false;
    this.loadPhotos();
  }

  onDeleted(id: number) {
    this.api.deleteMedia(id).subscribe(() => {
      this.photos = this.photos.filter(p => p.id !== id);
    });
  }

  logout() { this.auth.logout(); }
}
