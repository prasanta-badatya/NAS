import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';

import { GalleryRoutingModule } from './gallery-routing.module';
import { GalleryHomeComponent } from './gallery-home/gallery-home.component';
import { UploadComponent } from './upload/upload.component';
import { PhotoGridComponent } from './photo-grid/photo-grid.component';

@NgModule({
  declarations: [GalleryHomeComponent, UploadComponent, PhotoGridComponent],
  imports: [CommonModule, GalleryRoutingModule]
})
export class GalleryModule {}
