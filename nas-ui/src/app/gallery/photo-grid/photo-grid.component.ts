import { Component, EventEmitter, Input, Output } from '@angular/core';
import { DateGroup, MediaFile } from '../../shared/models/media.model';

@Component({
  selector: 'app-photo-grid',
  templateUrl: './photo-grid.component.html',
  styleUrls: ['./photo-grid.component.scss']
})
export class PhotoGridComponent {
  @Input() groups: DateGroup[] = [];
  @Input() selectMode = false;
  @Input() selectedIds = new Set<number>();

  @Output() photoClicked    = new EventEmitter<MediaFile>();
  @Output() longPressed     = new EventEmitter<MediaFile>();
  @Output() selectionToggled = new EventEmitter<number>();

  private pressTimers = new Map<number, ReturnType<typeof setTimeout>>();

  onTileClick(photo: MediaFile) {
    if (this.selectMode) {
      this.selectionToggled.emit(photo.id);
    } else {
      this.photoClicked.emit(photo);
    }
  }

  onTouchStart(photo: MediaFile) {
    const timer = setTimeout(() => {
      this.pressTimers.delete(photo.id);
      this.longPressed.emit(photo);
    }, 500);
    this.pressTimers.set(photo.id, timer);
  }

  onTouchEnd(photo: MediaFile) {
    const timer = this.pressTimers.get(photo.id);
    if (timer !== undefined) {
      clearTimeout(timer);
      this.pressTimers.delete(photo.id);
    }
  }
}
