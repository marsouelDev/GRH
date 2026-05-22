import { Component } from '@angular/core';
import { RouterModule } from '@angular/router';
import { CommonModule } from '@angular/common';
import { AuthService } from '../../services/auth/auth.service';

@Component({
  selector: 'app-side-bar',
  standalone: true,
  imports: [CommonModule, RouterModule],
  templateUrl: './side-bar.html',
  styleUrl: './side-bar.css',
})
export class SideBar {
  currentUser: { email: string; nom: string; prenom: string; role: string };

  constructor(private authService: AuthService) {
    this.currentUser = this.authService.getCurrentUser();
  }

  isAdmin(): boolean {
    return this.authService.isAdmin();
  }

  isRH(): boolean {
    return this.authService.isRH();
  }

  isAdminOrRH(): boolean {
    return this.authService.isAdmin() || this.authService.isRH();
  }

  getSidebarClass(): string {
    if (this.authService.isAdmin()) return 'sidebar sidebar--admin';
    if (this.authService.isRH()) return 'sidebar sidebar--rh';
    return 'sidebar sidebar--employe';
  }
}
