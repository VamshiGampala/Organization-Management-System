import { Component, OnInit } from '@angular/core';
import { Router, RouterModule } from '@angular/router';

@Component({
  selector: 'app-sidebar',
  templateUrl: './sidebar.component.html',
  styleUrls: ['./sidebar.component.scss']
})
export class SidebarComponent implements OnInit {
  role;
  roleStatus: Boolean;
  menuList = [{
    name: 'Dashboard',
    path: 'dashboard',
    icon: 'fa fa-home'
  }, {
    name: 'Employees',
    path: 'employees-list',
    icon: 'fa-solid fa-users'
  },
  {
    name: 'Clients',
    path: 'clients-list',
    icon: 'fa-sharp fa-solid fa-handshake'
  },
  {
    name: 'Vendors',
    path: 'vendors-list',
    icon: 'fa-solid fa-store'
  },
  {
    name: 'Projects',
    path: 'project-list',
    icon: 'fa-solid fa-sliders'
  },
  ]
  menuListForAdmin = [{
    name: 'Dashboard',
    path: 'dashboard',
    icon: 'fa fa-home'
  }, {
    name: 'Employees',
    path: 'employees-list',
    icon: 'fa-solid fa-users'
  },
  {
    name: 'Clients',
    path: 'clients-list',
    icon: 'fa-sharp fa-solid fa-handshake'
  },
  {
    name: 'Vendors',
    path: 'vendors-list',
    icon: 'fa-solid fa-store'
  },
  {
    name: 'Projects',
    path: 'project-list',
    icon: 'fa-solid fa-sliders'
  },
  ]

  menuListforResources = [{
    name: 'Dashboard',
    path: 'dashboard',
    icon: 'fa fa-home'
  },
  {
    name: 'Projects',
    path: 'project-list',
    icon: 'fa-solid fa-diagram-project'
  }, 


  ]
  menuListforApprovers = [{
    name: 'Dashboard',
    path: 'dashboard',
    icon: 'fa fa-home'
  },
  {
    name: 'Projects',
    path: 'project-list',
    icon: 'fa-solid fa-diagram-project'
  }, 


  ]
  constructor(private router: Router) { }

  ngOnInit(): void {
    this.roleStatus = true;
    this.role = localStorage.getItem('role');
    let timeApprover = localStorage.getItem('timeApprover');
    // if (this.role == 'Admin' && timeApprover === 'true') {
    //   this.roleStatus = true;
    // } else {
    //   this.roleStatus = false;
    // }

  }
  isActive(path: string): boolean {
    return this.router.url === '/' + path;
  }

}
