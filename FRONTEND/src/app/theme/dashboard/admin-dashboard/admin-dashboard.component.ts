import { HttpService } from 'src/app/services/http-service/http.service';
import { StaticDataEntity } from 'src/app/shared/static-data';
import { ActivatedRoute, Router } from '@angular/router';
import { ColumnApi, GridReadyEvent } from 'ag-grid-community';
import { ChangeDetectorRef, Component, EventEmitter, HostListener, OnInit, Output, ViewChild } from '@angular/core';
import { CustomDatePipe } from 'src/app/shared/datePipe/custom-date.pipe';
import { DatePipe } from '@angular/common';
import pdfmake from 'pdfmake/build/pdfmake';
import pdfFonts from 'pdfmake/build/vfs_fonts';
pdfmake.vfs = pdfFonts.pdfMake.vfs;
import * as moment from 'moment';
// import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { validateAllFormFields } from 'src/app/shared/utils/utils';
import { NotificationService } from 'src/app/services/notification-service/notification.service';
import { ToastService } from 'src/app/services/toast.service';
import { PageReloadService } from 'src/app/services/auto-reload/page-reload.service';
import { ApexNonAxisChartSeries, ApexChart, ApexResponsive } from 'ng-apexcharts';
export type ChartOptions = {
  series: ApexNonAxisChartSeries;
  chart: ApexChart;
  responsive: ApexResponsive[];
  labels: any;
};
@Component({
  selector: 'app-admin-dashboard',
  templateUrl: './admin-dashboard.component.html',
  styleUrls: ['./admin-dashboard.component.css']
})
export class AdminDashboardComponent implements OnInit {
  yourIdValueHere = 1;
  timeSheetList;
  timesheetColumnsDefs;
  pageNumber = 1;
  timesheetDetails;
  timesheetListData;
  viewColumns;
  projectColumnsDefs;
  status;
  public gridColumnApi: ColumnApi;
  private gridApi: any;
  private gridApiView: any;
  totalHours = 0;
  commentsForm:FormGroup;
  @Output() gridReadyEvent: EventEmitter<GridReadyEvent> = new EventEmitter<GridReadyEvent>();
  backgroundColors = ["#f0f0f0", "#F7FBFF"];
  @ViewChild('timesheetData') timesheetDataModal;
  @ViewChild('dashboardTimesheetDataModal') dashboardTimesheetDataModal;
  @ViewChild('ProjectList', { static: false }) ProjectList!: ChartOptions;
  @ViewChild('ResourcesbyProject', { static: false }) ResourcesbyProject!: ChartOptions;
  projectList;
  resourceDetails;
  public Mytickets: any;
  public ProjectsCount: any;
  public Resources: any;
  dates;
  startDate: any;
  endDate: any;
  startDate1:any;
  endDate1:any;
  dd: any;
  tableData: any;
  timesheetResourceDetails: any;
  role =localStorage.getItem('role');
  gridConfigurations: any[] = [];
  viewColumnsDefs: any[]; // Declare the array to hold column definitions
  gridConfig: { rowData: any; columnDefs: any[]; pagination: boolean; paginationPageSize: number; };
  timeSheetList1;
  timeSheetStatus: any;
  showApprove :Boolean = true;
  showReject:Boolean = true;
  showComments: boolean;
  rowDetails: any;
  addcomments:FormGroup;
  dashboardData: any;
  constructor(private inactivityService: PageReloadService,private httpservice: HttpService,private notificationService: NotificationService,private fb: FormBuilder, private piper: DatePipe, private router: Router, private customDatePipe: CustomDatePipe, private toast: ToastService) { 
    // this.commentsForm = this.fb.group({
    //   comments:['',Validators.required]
    // });
    this.addcomments = this.fb.group({
      comments:['', Validators.required]
    })
   
  }
  truncateText(text: string, words: number): string {
    const wordsArray = text.split(' ');
    if (wordsArray.length > words) {
      return wordsArray.slice(0, words).join(' ') + '...';
    }
    return text;
  }
  @HostListener('document:mousemove', ['$event'])
  @HostListener('document:keydown', ['$event'])

  onUserActivity(event: Event) {
    this.inactivityService.resetInactivityTimer();
  }
  ngOnInit(): void {
    this.inactivityService.startInactivityTimer();
    // this.calculateWeekDates();
    // if(this.role == 'Approver'){
    //   this.getApproversTimesheets();
    // }
    // if(this.role == 'Admin'){
    //   this.getAdminTimesheets();
    // }
    // this.getAdminTimesheets();

    // this.getTimeSheets();
    // this.getProjects();
    this.getVendorsData()
    this.getResources()
  }
  navigateToProjectTab() {
    this.router.navigate(['/project-list'], { queryParams: { id: '1' } });
  }

  getClientsData(result:any){
    console.log(result)
    let data=[]
    result.projects.forEach((ele:any)=>{
      data.push(ele.resources_count)
    })
    return data;
  }
  getCleintsNames(result:any){
    let data=[]
    result.projects.forEach((ele:any)=>{
      data.push(ele.project_name)
    })
    return data;
  }
  getResources(){
    this.httpservice.doGet('Dashboard').subscribe((data: any) => {
      console.log(data)
      this.dashboardData = data;
      this.Resources = {
        series: [
          {
            name: "",
            data: this.getClientsData(this.dashboardData)
          }
          
        ],
        chart: {
          type: "bar",
          height: 350
        },
        plotOptions: {
          bar: {
            horizontal: false,
            columnWidth: "35%",
            endingShape: "rounded"
          }
        },
        dataLabels: {
          enabled: false
        },
        stroke: {
          show: true,
          width: 2,
          colors: ["transparent"]
        },
        xaxis: {
          title: {
            text: "Projects",
          },
          categories: this.getCleintsNames(this.dashboardData)
        },
        yaxis: {
          title: {
            text: "Employees"
          }
        },
        fill: {
          opacity: 1
        },
        tooltip: {
          y: {
            formatter: function(val) {
              return val + " Employees";
            }
          }
        },
        colors:["#1CD0BB"]
      };
    })
    
  }
  getResourcesData(result:any){
    console.log(result)
    let data=[]
    result.clients.forEach((ele:any)=>{
      data.push(ele.projects_count)
    })
    return data;
  }
  getResourcesNames(result:any){
    let data=[]
    result.clients.forEach((ele:any)=>{
      data.push(ele.client_name)
    })
    return data;
  }
  getVendorsData(){
    this.httpservice.doGet('Dashboard').subscribe((data: any) => {
      console.log(data)
      this.dashboardData = data;
      this.ProjectsCount = {
        series: [
          {
            name: "",
            data: this.getResourcesData(this.dashboardData)
          }
          
        ],
        chart: {
          type: "bar",
          height: 350
        },
        plotOptions: {
          bar: {
            horizontal: false,
            columnWidth: "35%",
            endingShape: "rounded",
          }
        },
        dataLabels: {
          enabled: false
        },
        stroke: {
          show: true,
          width: 2,
          colors: ["transparent"]
        },
        xaxis: {
          title: {
            text: "Clients",
          },
          categories: this.getResourcesNames(this.dashboardData) 
        },
        yaxis: {
          title: {
            text: "Projects"
          }
        },
        fill: {
          opacity: 1
        },
        tooltip: {
          y: {
            formatter: function(val) {
              return val + " Projects";
            }
          }
        },
        colors:["#654C8D"]
      };
    })
    
  }
  
  getStatusColor(status) {
    if (status == 'NotSubmitted') {
      return '#bf9000';
    }
    if (status == 'Submitted') {
      return "green";
    }
    if (status == 'Approved') {
      return "#3F51B5";
    }
    if (status == 'Rejected') {
      return "red";
    }
    if (status == 'Saved') {
      return "#674ea7";
    }
  }

  hideModal() {
    // this.commentsForm.reset();
    this.timesheetDataModal.hide();
  }
  hideDashboardModal() {
    this.addcomments.reset();
    this.dashboardTimesheetDataModal.hide();
  }
  submit() {
  
    let payload = {
      // resource_id: this.rowDetails.resource_id,
      // project_id: this.rowDetails.project_id,
      start_date: this.startDate1,
      end_date: this.endDate1,
      role:localStorage.getItem('role')
    }
    // this.dataSource.getRows = (params: IGetRowsParams) => {
      this.httpservice.doPost(`dashboardApprovalApi?pageNumber=${Number(this.pageNumber)}&pageSize=${Number(10)}`, payload).subscribe((result) => {
        this.timeSheetList1 = result.results;
        if (result.results?.length === 0) {
          this.gridApi.showNoRowsOverlay(); // Show "No data to show" message
        } else {
          this.gridApi.hideOverlay(); // Hide the overlay message
        }
        // params.successCallback(result.results, result.total_records);
  
      })
    // }
    // this.gridApi.setDatasource(this.dataSource);
  }
  @HostListener('document:keydown.escape', ['$event']) onKeydownHandler(event: KeyboardEvent) {
    this.addcomments.reset();
  }

  approve(type) {
    if(this.addcomments.valid){
      let todayDate = new Date();
      const approverComments = this.addcomments.get('comments')?.value;
      let payload = {
        resource_id: this.rowDetails.resource_id,
        project_id: this.rowDetails.project_id,
        start_date: this.rowDetails.start_date,
        end_date: this.rowDetails.end_date,
        approver_comments : approverComments,
        approved_date: this.piper.transform(todayDate, 'yyyy-MM-dd'),
      };
  
      if (type === 'Approve') {
        payload['status'] = 'Approved';
      } else {
        payload['status'] = 'Rejected';
      }
      this.httpservice.doPost(StaticDataEntity.approveOrReject, payload).subscribe((result) => {
        if(result.message){
          // this.notificationService.showSucessNotification("Success",result.message);
          this.toast.showSuccess("success", "Success", result.message);
          this.dashboardTimesheetDataModal.hide();
          this.submit();
          this.addcomments.patchValue({
            comments:'',
          })
        }
      });
    }else{
      validateAllFormFields(this.addcomments);
    }
  }

  editTimesheet(params: any) {
    this.router.navigate(['/myTimeSheet'], {
      queryParams: {
        startDate: params.start_date,
        endDate: params.end_date,
        status: 2
      }

    });

  }

  calculateWeekDates() {
    const currentDate = moment();
    const currentDay = currentDate.day(); // 0 (Sunday) to 6 (Saturday)
    const startOfWeek = moment(currentDate).startOf('isoWeek');
    const endOfWeek = moment(currentDate).endOf('isoWeek');
  
    // Set the time from currentDate to startOfWeek
    startOfWeek.set({
      hour: currentDate.hours(),
      minute: currentDate.minutes(),
      second: currentDate.seconds()
    });
  
    // Set the time from currentDate to endOfWeek
    endOfWeek.set({
      hour: currentDate.hours(),
      minute: currentDate.minutes(),
      second: currentDate.seconds()
    });
  
    this.startDate1 = startOfWeek.format('YYYY-MM-DD');
    this.endDate1 = endOfWeek.format('YYYY-MM-DD');
  }

  getApproversTimesheets(){
    let payload = {
      "start_date": this.startDate1,
      "end_date": this.endDate1,
      "project_id": null,
      "resource_id": null,
    }
    this.httpservice.doPost(`approverApproveTimesheets?pageNumber=${Number(this.pageNumber)}&pageSize=${Number(10)}`, payload).subscribe((result)=>{
      this.timeSheetList1 = result.results;
    })
  }
  getAdminTimesheets(){
    let payload = {
      "start_date": this.startDate1,
      "end_date": this.endDate1,
      "role": localStorage.getItem('role')
    }
    this.httpservice.doPost(`dashboardApprovalApi?pageNumber=${Number(this.pageNumber)}&pageSize=${Number(10)}`, payload).subscribe((result)=>{
      this.timeSheetList1 = result.results;
    })
  }

  viewTimesheet(data) {
    let payload = {
      "resource_id": localStorage.getItem('userId'),
      "start_date": data.start_date,
      "end_date": data.end_date
    }
    this.httpservice.doPost(StaticDataEntity.viewMytimesheet, payload).subscribe((result: any) => {
      this.timesheetDetails = result.timesheets;
      this.timesheetDetails.forEach(element => {
        element.work_hour = Number(element.work_hour)
        this.totalHours = this.totalHours + element.work_hour
      });
    })

  }
  getProjects() {
    this.httpservice.doGet(StaticDataEntity.myProjectsList).subscribe((result: any) => {
      this.projectList = result;
    })
  }
  getTimeSheets() {
    let payload = {
      "start_date": null,
      "end_date": null,
      "current_date" :moment(new Date ()).format('YYYY-MM-DD')

    }
    this.httpservice.doPost(StaticDataEntity.myTimesheets, payload).subscribe((result: any) => {
      this.timeSheetList = result;
    }
    )
  }



  getResourceDetails() {
    this.httpservice.doGet(StaticDataEntity.getResourceByID.replace(/{id}/g, localStorage.getItem('userId'))).subscribe((result) => {
      this.resourceDetails = result;
    })
  }

  onGridReady(event: GridReadyEvent): void {
    this.gridReadyEvent.emit(event);
    this.gridApi = event.api;
    this.gridColumnApi = event.columnApi;
    this.gridApi.sizeColumnsToFit();
    this.gridApi.setDomLayout('autoHeight');
    window.onresize = () => {
      this.gridApi.sizeColumnsToFit();
  }
  }
  showModal(data) {
    // Clear the grid configurations array before populating with new data
    this.gridConfigurations = [];
  
    // Call the getMyTimesheetView function to retrieve data for the grids
    this.getMyTimesheetView(data);
    
  }
  showDashboardTimesheets(data){
    this.gridConfigurations = [];
    this.timeSheetStatus = data.status
    this.rowDetails = data;
  this.dashboardTimesheetDataModal.show();
  if(this.timeSheetStatus === 'Approved'){
    this.showApprove = false;
    this.showReject = false;
    this.showComments = false;

  }else if(this.timeSheetStatus === 'Rejected'){
    this.showReject = false;
    this.showApprove = false;
    this.showComments = false;
  }else if (this.timeSheetStatus === 'Submitted' || this.timeSheetStatus === 'NotSubmitted' || this.timeSheetStatus === 'Saved'){
    this.showApprove = true;
    this.showReject = true;
    this.showComments = true;
  }
    this.viewDashboardTimesheet(data)
    this.viewColumns = [
      { headerName: 'Date', field: 'ts_date', sortable: true, suppressSizeToFit: true, width: 150,
      valueGetter:(params)=>{
        return this.customDatePipe.transform(params.data.ts_date);
      },
      tooltipValueGetter:(params:any)=>{
        return this.customDatePipe.transform(params.data.ts_date);
      }
    },
      { headerName: 'Start Time', field: 'ts_start_time', tooltipField:'ts_start_time', sortable: true, suppressSizeToFit: true, width: 100 },
      { headerName: 'Meal Start', field: 'meal_start_time', tooltipField:'meal_start_time', sortable: true, suppressSizeToFit: true, width: 100 },
      { headerName: 'Meal End', field: 'meal_end_time', tooltipField:'meal_end_time', sortable: true, suppressSizeToFit: true, width: 100 },
      { headerName: 'End Time', field: 'ts_end_time', tooltipField:'ts_end_time', sortable: true, suppressSizeToFit: true, width: 100 },
      { headerName: 'Work Hours', field: 'work_hour', tooltipField:'work_hour', sortable: true, suppressSizeToFit: true, width: 100 },
      // { headerName: 'Project Name', field: 'project_name', sortable: true, suppressSizeToFit: true, width: 170 },
      { headerName: 'Approver Name', field: 'approver_name', tooltipField:'approver_name', sortable: true, suppressSizeToFit: true, width: 180 },
  
      { headerName: 'Status', field: 'status', tooltipField:'status', sortable: true, suppressSizeToFit: true, width: 100, cellRenderer: (params: any) => {
        if (params.data?.status === 'Submitted') {
          return'<span style="color: green;">Submitted</span>';
        }
        if (params.data?.status === 'Approved' ) {
          return '<span style="color: #3F51B5;">Approved</span>'
        }
        if(params.data?.status === 'Rejected'){
          return '<span style="color: red;">Rejected</span>';
        }
        if(params.data?.status === 'NotSubmitted'){
          return '<span style="color: #bf9000;">Pending Submission</span>';
        }
        if(params.data?.status === 'Saved'){
          return '<span style= "color: #674ea7;">Pending Submission</span>';
        }
      } },
      {
        headerName: 'Activity',
        field: 'comments',
        sortable: true,
        suppressSizeToFit: true,
        width: 100,
        tooltipField: 'comments',
        valueFormatter: function (params) {
          if (params.value && params.value.length > 10) {
            return params.value.substring(0, 10) + '...';
          }
          return params.value; 
        },
      },
  
  
    ]
  }

  viewDashboardTimesheet(data) {
    let payload = {
      "resource_id": data.resource_id,
      "project_id": data.project_id,
      "start_date": data.start_date,
      "end_date": data.end_date,
    }
    this.httpservice.doPost(StaticDataEntity.viewResourceTimesheet, payload).subscribe((result: any) => {
      this.totalHours = 0;
      this.timesheetResourceDetails = result.resource_details;
      this.timesheetListData = result.timesheets;
      this.timesheetListData.forEach(element => {
        element.work_hour = Number(element.work_hour)
        this.totalHours = this.totalHours + element.work_hour
      });
    })
  
  }

  getMyTimesheetView(row) {
    let payload = {
      "start_date": row.start_date,
      "end_date": row.end_date
    };
  
    this.httpservice.doPost(StaticDataEntity.myTimesheetView, payload).subscribe((response) => {

      response.forEach((data) => {
        this.gridConfig = {
          rowData: data,
          columnDefs: this.viewColumnsDefs,
          pagination: true,
          paginationPageSize: 10
        };

  
        this.gridConfigurations.push(this.gridConfig); // Add the grid configuration to the array
      });
  
      // Show the modal after receiving the data and configuring the grids
      this.timesheetDataModal.show();
    });
  }

 
}
