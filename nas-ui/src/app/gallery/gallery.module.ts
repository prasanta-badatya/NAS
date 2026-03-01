import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';

import { GalleryRoutingModule } from './gallery-routing.module';
import { GalleryHomeComponent } from './gallery-home/gallery-home.component';
import { UploadComponent } from './upload/upload.component';
import { PhotoGridComponent } from './photo-grid/photo-grid.component';
import { ViewerComponent } from './viewer/viewer.component';
import { TrashComponent } from './trash/trash.component';
import { ConfirmDialogComponent } from '../shared/confirm-dialog/confirm-dialog.component';

@NgModule({
  declarations: [
    GalleryHomeComponent,
    UploadComponent,
    PhotoGridComponent,
    ViewerComponent,
    TrashComponent,
    ConfirmDialogComponent,
  ],
  imports: [CommonModule, RouterModule, GalleryRoutingModule]
})
export class GalleryModule {}
