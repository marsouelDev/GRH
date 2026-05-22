import { Component } from '@angular/core';
import { RouterModule } from '@angular/router';
import { CommonModule } from '@angular/common';
import { AuthService } from '../../services/auth/auth.service';

@Component({
  selector: 'app-nav-bar',
  standalone: true,
  imports: [CommonModule, RouterModule],
  templateUrl: './nav-bar.html',
  styleUrl: './nav-bar.css',
})
export class NavBar {
  currentUser: { email: string; nom: string; prenom: string; role: string };

  constructor(private authService: AuthService) {
    this.currentUser = this.authService.getCurrentUser();
  }

  getInitiales(): string {
    const nom = this.currentUser.nom?.charAt(0)?.toUpperCase() || '';
    const prenom = this.currentUser.prenom?.charAt(0)?.toUpperCase() || '';
    return prenom + nom;
  }

  getRoleLabel(): string {
    const role = this.currentUser.role;
    if (role === 'ADMIN') return 'Administrateur système';
    if (role === 'RH') return 'Responsable RH';
    return 'Employé';
  }

  getAvatarClass(): string {
    const role = this.currentUser.role;
    if (role === 'ADMIN') return 'navbar__avatar navbar__avatar--admin';
    if (role === 'RH') return 'navbar__avatar navbar__avatar--rh';
    return 'navbar__avatar navbar__avatar--employe';
  }

  getRoleBadgeClass(): string {
    const role = this.currentUser.role;
    if (role === 'ADMIN') return 'navbar__role-badge navbar__role-badge--admin';
    if (role === 'RH') return 'navbar__role-badge navbar__role-badge--rh';
    return 'navbar__role-badge navbar__role-badge--employe';
  }

  seDeconnecter(): void {
    if (confirm('Voulez-vous vraiment vous déconnecter ?')) {
      this.authService.logout();
    }
  }
}
