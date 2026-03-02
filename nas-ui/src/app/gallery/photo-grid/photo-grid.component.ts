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

  @Output() photoClicked     = new EventEmitter<MediaFile>();
  @Output() longPressed      = new EventEmitter<MediaFile>();
  @Output() selectionToggled = new EventEmitter<number>();
  @Output() rangeSelected    = new EventEmitter<number[]>();

  // Tracks last touched item for Shift+Click range anchor
  private lastSelectedId: number | null = null;

  // ── Click handler (desktop: plain / Ctrl / Shift) ──────────────────────────
  onTileClick(photo: MediaFile, event: MouseEvent) {
    // Shift+Click — select a range from last selected to this item
    if (event.shiftKey && this.selectMode && this.lastSelectedId !== null) {
      this.doRangeSelect(photo);
      return;
    }

    // Ctrl/Cmd+Click — toggle this item; enters select mode if needed
    if (event.ctrlKey || event.metaKey) {
      this.lastSelectedId = photo.id;
      if (!this.selectMode) {
        this.longPressed.emit(photo);   // parent enters select mode & selects photo
      } else {
        this.selectionToggled.emit(photo.id);
      }
      return;
    }

    // Normal click
    if (this.selectMode) {
      this.lastSelectedId = photo.id;
      this.selectionToggled.emit(photo.id);
    } else {
      this.photoClicked.emit(photo);
    }
  }

  // ── Right-click — enter select mode and select the item ───────────────────
  onRightClick(event: MouseEvent, photo: MediaFile) {
    event.preventDefault();
    this.lastSelectedId = photo.id;
    if (!this.selectMode) {
      this.longPressed.emit(photo);
    } else {
      this.selectionToggled.emit(photo.id);
    }
  }

  // ── Long-press (mobile touch) ──────────────────────────────────────────────
  private pressTimers = new Map<number, ReturnType<typeof setTimeout>>();

  onTouchStart(photo: MediaFile) {
    const timer = setTimeout(() => {
      this.pressTimers.delete(photo.id);
      this.lastSelectedId = photo.id;
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

  // ── Range selection helper ─────────────────────────────────────────────────
  private doRangeSelect(to: MediaFile) {
    const flat = this.groups.flatMap(g => g.photos);
    const fromIdx = flat.findIndex(p => p.id === this.lastSelectedId);
    const toIdx   = flat.findIndex(p => p.id === to.id);
    if (fromIdx === -1 || toIdx === -1) return;

    const [start, end] = fromIdx < toIdx ? [fromIdx, toIdx] : [toIdx, fromIdx];
    const ids = flat.slice(start, end + 1).map(p => p.id);
    this.lastSelectedId = to.id;
    this.rangeSelected.emit(ids);
  }
}
