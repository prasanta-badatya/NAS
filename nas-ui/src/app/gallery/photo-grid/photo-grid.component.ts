import { Component, Input, Output, EventEmitter } from '@angular/core';

@Component({
  selector: 'app-photo-grid',
  templateUrl: './photo-grid.component.html',
  styleUrls: ['./photo-grid.component.scss']
})
export class PhotoGridComponent {
  @Input() photos: any[] = [];
  @Output() deleted = new EventEmitter<number>();

  lightbox: any = null;

  open(photo: any) { this.lightbox = photo; }
  close() { this.lightbox = null; }

  delete(id: number) {
    this.deleted.emit(id);
    if (this.lightbox?.id === id) this.lightbox = null;
  }
}
