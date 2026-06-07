import { Component } from '@angular/core';
import { AuthService } from '../../services/auth/auth.service';
import { DashboardEmploye } from "../employe/dashboard-employe/dashboard-employe";
import { DashboardRh } from "../rh/dashboard-rh/dashboard-rh";
import { DashboardAdmin } from "../admin/dashboard-admin/dashboard-admin";
import { NgIf } from '@angular/common';

@Component({
  selector: 'app-dashboard',
  imports: [DashboardEmploye, DashboardRh, DashboardAdmin,NgIf],
  templateUrl: './dashboard.html',
  styleUrl: './dashboard.css',
})
export class Dashboard {
  role = '';

  constructor(private authService: AuthService) {
    this.role = this.authService.getRole();
  }
}
