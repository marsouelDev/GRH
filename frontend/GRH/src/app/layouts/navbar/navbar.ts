import { Component, OnInit, inject, output } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ThemeService } from '../../services/Theme/theme-service';
import { AuthService } from '../../services/auth/auth.service';
import { LayoutService } from '../../services/layoutService/layout.service';
import { NotificationService } from '../../services/notification/notification-services';
import { RouterLink } from '@angular/router';

@Component({
  selector: 'app-navbar',
  standalone: true,
  imports: [CommonModule, RouterLink],
  templateUrl: './navbar.html',
  styleUrl: './navbar.css',
  host: { class: 'app-navbar' },
})
export class Navbar implements OnInit {
  public theme = inject(ThemeService);
  public authService = inject(AuthService);
  private layoutService = inject(LayoutService);
  private notifService = inject(NotificationService);

  badgeCount = 0;

  // ✅ Output proprement déclaré
  menuToggle = output<void>();

  ngOnInit(): void {
    this.notifService.nonLuesCount$.subscribe((count) => {
      this.badgeCount = count;
    });

    this.notifService.getNotifications('false').subscribe({
      next: (nonLues) => this.notifService.mettreAJourCompteur(nonLues),
    });
  }

  onMenuToggle(): void {
    this.menuToggle.emit();
  }

  onLogout(): void {
    this.authService.logout();
  }

  getUserFullName(): string {
    const user = this.authService.getCurrentUser();
    if (!user) return '';
    const prenom = user.prenom?.trim() ?? '';
    const nom = user.nom?.trim() ?? '';
    return `${prenom} ${nom}`.trim();
  }

  getRoleLabel(): string {
    if (this.authService.isAdmin()) return 'Admin';
    if (this.authService.isRH()) return 'Ressources Humaines';
    return 'Employé';
  }

  getRoleClass(): string {
    if (this.authService.isAdmin()) return 'role-admin';
    if (this.authService.isRH()) return 'role-rh';
    return 'role-employe';
  }

  getInitials(): string {
    const user = this.authService.getCurrentUser();
    if (!user) return '??';

    const p = user.prenom?.charAt(0)?.toUpperCase() ?? '';
    const n = user.nom?.charAt(0)?.toUpperCase() ?? '';

    const initials = p + n;
    return initials || '??';
  }
}
