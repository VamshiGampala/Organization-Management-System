import { NgModule } from '@angular/core';
import { CommonModule, DatePipe } from '@angular/common';
import { ResourcesRoutingModule } from './resources-routing.module';
import { ResourceListComponent } from './resource-list/resource-list.component';
import { AddResourceComponent } from './add-resource/add-resource.component';
import { AgGridModule } from 'ag-grid-angular';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { NgMultiSelectDropDownModule } from "ng-multiselect-dropdown";
import { ResourceViewComponent } from './resource-view/resource-view.component';
import { ModalModule } from 'ngx-bootstrap/modal';
import { BsDatepickerModule, BsDatepickerConfig } from 'ngx-bootstrap/datepicker';
import { SharedModule } from 'src/app/shared/shared/shared.module';
import {ToastModule} from "primeng/toast"
import { NgbPaginationModule } from '@ng-bootstrap/ng-bootstrap';
import { NgbModule } from '@ng-bootstrap/ng-bootstrap';

@NgModule({
  declarations: [
    ResourceListComponent,
    AddResourceComponent,
    ResourceViewComponent,
    
    
    
  ],
  imports: [
    SharedModule,
    CommonModule,
    ResourcesRoutingModule,
    AgGridModule,
    BsDatepickerModule.forRoot(),
    FormsModule, ReactiveFormsModule,NgMultiSelectDropDownModule.forRoot(),ModalModule.forRoot(),
    ToastModule,
    NgbPaginationModule,
    NgbModule
    

  ],
  providers:[DatePipe]
})
export class ResourcesModule { }
