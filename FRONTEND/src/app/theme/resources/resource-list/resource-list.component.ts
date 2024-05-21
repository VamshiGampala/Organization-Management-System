
import { StaticDataEntity } from 'src/app/shared/static-data';
import { Router } from '@angular/router';
import { Component, EventEmitter, HostListener, OnInit, Output } from '@angular/core';
import { ColumnApi, GridOptions, GridReadyEvent,IDatasource,IGetRowsParams } from 'ag-grid-community';
import { HttpService } from 'src/app/services/http-service/http.service';
import { HttpParams } from '@angular/common/http';
import { PageReloadService } from 'src/app/services/auto-reload/page-reload.service';
import { NgbPaginationConfig } from '@ng-bootstrap/ng-bootstrap';
interface Country {
  id?: number;
  name: string;
  flag: string;
  area: number;
  population: number;
}
const COUNTRIES: Country[] = [
  {
    name: 'Russia',
    flag: 'f/f3/Flag_of_Russia.svg',
    area: 17075200,
    population: 146989754
  },
  {
    name: 'France',
    flag: 'c/c3/Flag_of_France.svg',
    area: 640679,
    population: 64979548
  },
  {
    name: 'Germany',
    flag: 'b/ba/Flag_of_Germany.svg',
    area: 357114,
    population: 82114224
  },
  {
    name: 'Portugal',
    flag: '5/5c/Flag_of_Portugal.svg',
    area: 92090,
    population: 10329506
  },
  {
    name: 'Canada',
    flag: 'c/cf/Flag_of_Canada.svg',
    area: 9976140,
    population: 36624199
  },
  {
    name: 'Vietnam',
    flag: '2/21/Flag_of_Vietnam.svg',
    area: 331212,
    population: 95540800
  },
  {
    name: 'Brazil',
    flag: '0/05/Flag_of_Brazil.svg',
    area: 8515767,
    population: 209288278
  },
  {
    name: 'Mexico',
    flag: 'f/fc/Flag_of_Mexico.svg',
    area: 1964375,
    population: 129163276
  },
  {
    name: 'United States',
    flag: 'a/a4/Flag_of_the_United_States.svg',
    area: 9629091,
    population: 324459463
  },
  {
    name: 'India',
    flag: '4/41/Flag_of_India.svg',
    area: 3287263,
    population: 1324171354
  },
  {
    name: 'Indonesia',
    flag: '9/9f/Flag_of_Indonesia.svg',
    area: 1910931,
    population: 263991379
  },
  {
    name: 'Tuvalu',
    flag: '3/38/Flag_of_Tuvalu.svg',
    area: 26,
    population: 11097
  },
  {
    name: 'China',
    flag: 'f/fa/Flag_of_the_People%27s_Republic_of_China.svg',
    area: 9596960,
    population: 1409517397
  }
];

@Component({
  selector: 'app-resource-list',
  templateUrl: './resource-list.component.html',
  styleUrls: ['./resource-list.component.css']
})

export class ResourceListComponent implements OnInit {
  resourceList: any;
  rowData = [];
  type:string = "All";
  resourcesColumnDefs: any;
  private gridApi: any;
  searchText;
  public gridColumnApi: ColumnApi;
  
  gridOptions: GridOptions = {
    pagination: true,
    rowModelType: 'infinite',
    cacheBlockSize: 10, // you can have your custom page size
    paginationPageSize: 10, //pagesize
    columnDefs: [
      { headerName: 'Resource ID', field: 'resource_details.resource_number', tooltipField:'resource_details.resource_number', sortable: true, suppressSizeToFit: true, width: 120 },
      { headerName: 'Candidate Name', field: 'resource_details.first_name+resource_details.last_name', tooltipField:'resource_details.first_name+resource_details.last_name', sortable: true, suppressSizeToFit: true, width: 200,   },
      { headerName: 'Email Id', field: 'resource_details.email_id', tooltipField:'resource_details.email_id', sortable: true, suppressSizeToFit: true, width: 210 },
      { headerName: 'Phone Number', field: 'resource_details.primary_phone_number', tooltipField:'resource_details.primary_phone_number', sortable: true, suppressSizeToFit: true, width: 170 },
      {
        headerName: 'Projects',
        field: 'resource_projects',
        sortable: true,
        suppressSizeToFit: true,
        width: 150,
        cellRenderer: (params: any) => {
          const projects = params.value;
          if (projects && projects.length > 0) {
            return projects.map((project: any) => project.project_name).join(', ');
          } else {
            return '';
          }
        },
        tooltipValueGetter:(params:any)=>{
          const projects = params.value;
          if (projects && projects.length > 0) {
            return projects.map((project: any) => project.project_name).join(', ');
          } else {
            return '';
          }
        }
      },
      { headerName: 'Resource Status', field: 'resource_details.status', cellStyle: { 'text-align': 'center' }, tooltipField:'resource_details.status', sortable: true, suppressSizeToFit: true, width: 120, cellRenderer:(params)=>{
        const status = params.value;
        // const cellValue = status === 'Active' ? '<span style="color: #3F51B5;">Active</span>' : '<span style="color: red;">Inactive</span>';
        // return cellValue;
        if(status === 'Active'){
          return '<span style="color: black; background-color: lightgreen; border-radius: 3px; padding:5px 15px; border: 1px solid #fff;">Active</span>'
        }
        if(status === 'Inactive'){
          return '<span style="color: red; background-color: rgb(247, 227, 227,0.5) ; border-radius: 3px; padding:5px 15px; border: 1px solid red;">Inactive</span>';
        }
      } },
      // { headerName: 'First Name', field: 'resource_details.first_name', tooltipField:'resource_details.first_name', sortable: true, suppressSizeToFit: true, width: 120 },
      // { headerName: 'Last Name', field: 'resource_details.last_name', tooltipField:'resource_details.last_name', sortable: true, suppressSizeToFit: true, width: 100 },
      
      
      { headerName: 'Employment Type', field: 'resource_details.employement_type.type', tooltipField:'resource_details.employement_type.type', sortable: true, suppressSizeToFit: true, width: 150 },
      {
        headerName: 'Actions',
        field: 'resource_details.status',
        // tooltipField:'resource_details.status',
        sortable: true,
        suppressSizeToFit: true,
        width: 116,
        cellRenderer: (params: any) => {
          if(params.data){
            // return '<i class="fa fa-eye" style="cursor: pointer; margin-right: 5px;" data-toggle="tooltip" data-placement="top" title="View Resource"></i>'
            // return "<img class='edit-view' width='32px' style='cursor:pointer' data-toggle='tooltip' data-placement='top' title='View/ Edit resource' src='../../../../assets/images/editview.png'>"
            return "<i data-toggle='tooltip' data-placement='top' title='Edit resource' style='margin-right:10px; cursor: pointer; font-size: 17px;'' class='edit fa-solid fas fa-file-pen'></i> <i class='view mr-1 fa-solid fa-file-lines'  style='cursor:pointer; font-size:17px' alt='fine-print--v1' data-toggle='tooltip' data-placement='top' title='View resource'></i>" 
          }
                //  '<i class="fa fa-pencil-square-o" style="cursor: pointer;"></i>';
        },
        onCellClicked: (params: any) => {
          const iconName = params.event.target.className;
          if (iconName.includes('view')) {
            let resourceId = params.data.resource_details.id;
            this.router.navigate(['/employees-list', 'view-employee', resourceId, 'view']);
          } else if (iconName.includes('edit')) {
            let resourceId = params.data.resource_details.id;
            this.router.navigate(['/employees-list', 'view-employee', resourceId, 'edit']);
          }
        }
      }
      
    ],
  };
  displayedResources: Country[];
  viewResource(event:any,id:any){
    console.log(event,id)
    if (event==='view') {
      this.router.navigate(['/employees-list', 'view-employee', id, 'view']);
    } else if (event==='edit') {
      this.router.navigate(['/employees-list', 'view-employee', id, 'edit']);
    }
  }
  dataSource: IDatasource = {
    getRows: (params: IGetRowsParams) => {
      const payload = {
        status: this.type,
        search_key: this.searchText ? this.searchText : ''
      };
  
      this.doPostRequest(payload).subscribe((result) => {
        this.resourceList = result;
        if (result.resource_list?.length === 0) {
          this.gridApi.showNoRowsOverlay(); // Show "No data to show" message
        } else {
          this.gridApi.hideOverlay(); // Hide the overlay message
        }
        params.successCallback(result.resource_list, result.total_count);
      });
    }
  };
  // allResources: any;
  
  doPostRequest(payload: any) {
    return this.httpservice.doPost(`allResourcesByStatus?pageNumber=${Number(this.pageNumber)}&pageSize=${Number(10)}`, payload);
  }
  
  getList(type: string) {
    this.type = type;
    return this.doPostRequest({ status: type });
  }
  
  getResourceList(type: string) {
    this.type = type;
    this.searchText = "";
    const payload = {
      status: this.type,
      search_key: this.searchText ? this.searchText : ""
    };
  
    this.doPostRequest(payload).subscribe((result) => {
      this.resourceList = result;
      this.allResources = result.resource_list
      this.refreshCountries();
      if (this.gridApi) {
        this.gridApi.setDatasource(this.dataSource);
        this.gridApi.setFilterModel(null); // Clear any existing filter model
  
        if (result.resource_list?.length === 0) {
          this.gridApi.showNoRowsOverlay(); // Show "No data to show" message
        } else {
          this.gridApi.hideOverlay(); // Hide the overlay message
        }
      }
    });
  }

  @Output() gridReadyEvent: EventEmitter<GridReadyEvent> = new EventEmitter<GridReadyEvent>();
  pageNumber= 1;
  allResources: any[] = [];
  page = 1;
  pageSize = 10;
  collectionSize ;
  countries: Country[];
  constructor(config: NgbPaginationConfig,private inactivityService: PageReloadService,private httpservice: HttpService, private router:Router) { 
    // config.size = 'sm';
    // config.boundaryLinks = true;
    
  }
  refreshCountries() {
    this.displayedResources = this.allResources
    .map((client, i) => ({ id: i + 1, ...client }))
    .slice((this.page - 1) * this.pageSize, (this.page - 1) * this.pageSize + this.pageSize);
    console.log(this.allResources)
  }
  
  

  ngOnInit(): void {
    // this.getResource();
    this.getResourceList("All");
    // this.collectionSize = this.allResources.length
    this.getList("All");
    this.inactivityService.startInactivityTimer();
  }
  
  @HostListener('document:mousemove', ['$event'])
  @HostListener('document:keydown', ['$event'])

  onUserActivity(event: Event) {
    this.inactivityService.resetInactivityTimer();
  }

  onGridReady(event: GridReadyEvent): void {
    this.gridReadyEvent.emit(event);
    this.gridApi = event.api;
    this.gridColumnApi = event.columnApi;
    this.gridApi.sizeColumnsToFit();
    this.gridApi.setDomLayout('autoHeight');
    this.gridApi.setDatasource(this.dataSource)
    window.onresize = () => {
      this.gridApi.sizeColumnsToFit();
  }
  }

  getResource() {
    let payload = {
      status: 'All', 
    };
      this.httpservice.doPost(`allResourcesByStatus?pageNumber=${Number(this.pageNumber)}&pageSize=${Number(10)}`, payload).subscribe((result) => {
        this.resourceList = result;
   
    });
  }  
   
  search() {
    const payload = {
      status: this.type,
      search_key: this.searchText ? this.searchText : ''
    };
    console.log(payload)
    this.doPostRequest(payload).subscribe((result) => {
      // this.allResources = result.resource_list;
      // result.resource_list.forEach((ele:any) => {
      //   this.displayedResources.push(ele)
      // });
      this.displayedResources = result.resource_list
      // this.gridApi.setDatasource(this.dataSource);
    });
  }
  
  
  
  onPaginationChanged(event: any): void {
    // Check if the event is triggered by user interaction
    if (event.api.paginationGetCurrentPage() !== undefined) {
      const pageNumber = event.api.paginationGetCurrentPage() + 1;
      if (this.pageNumber !== pageNumber) {
        this.pageNumber = pageNumber;
        this.getResource();
      }
    }
  }
 
}