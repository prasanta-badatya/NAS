import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { GalleryHomeComponent } from './gallery-home/gallery-home.component';
import { TrashComponent } from './trash/trash.component';

const routes: Routes = [
  { path: '', component: GalleryHomeComponent },
  { path: 'trash', component: TrashComponent },
];

@NgModule({
  imports: [RouterModule.forChild(routes)],
  exports: [RouterModule]
})
export class GalleryRoutingModule {}
