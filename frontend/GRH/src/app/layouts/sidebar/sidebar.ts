import { Component, effect, inject, OnDestroy, OnInit, signal } from '@angular/core';
import { Router, RouterLink, RouterLinkActive, NavigationEnd } from '@angular/router';
import { CommonModule } from '@angular/common';
import { filter, Subscription } from 'rxjs';

import { AuthService } from '../../services/auth/auth.service';
import { LayoutService } from '../../services/layoutService/layout.service';
import { ThemeService } from '../../services/Theme/theme-service';

@Component({
  selector: 'app-sidebar',
  standalone: true,
  imports: [RouterLink, RouterLinkActive, CommonModule],
  templateUrl: './sidebar.html',
  styleUrl: './sidebar.css',
})
export class Sidebar implements OnInit, OnDestroy {
  authService = inject(AuthService);
  private layout = inject(LayoutService);
  private router = inject(Router);
  private themeService = inject(ThemeService);

  isMobileOpen = signal(false);
  private routerSub!: Subscription;

  constructor() {
    effect(() => this.isMobileOpen.set(this.layout.sidebarOpen()));
  }

  ngOnInit(): void {
    this.routerSub = this.router.events
      .pipe(filter((e) => e instanceof NavigationEnd))
      .subscribe(() => {
        if (this.layout.sidebarOpen()) this.layout.closeSidebar();
      });
  }

  ngOnDestroy(): void {
    this.routerSub?.unsubscribe();
  }

  closeMobile(): void {
    this.layout.closeSidebar();
  }

  onLogout(): void {
    this.authService.logout();
    this.closeMobile();
  }

  getRoleLabel(): string {
    if (this.authService.isAdmin()) return 'Administrateur';
    if (this.authService.isRH()) return 'Responsable RH';
    if (this.authService.isEmploye()) return 'Employé';
    return '';
  }

  getUserName(): string {
    const u = this.authService.getCurrentUser();
    return `${u?.prenom ?? ''} ${u?.nom ?? ''}`.trim() || 'Utilisateur';
  }

  getInitials(): string {
    const u = this.authService.getCurrentUser();
    const p = u?.prenom?.[0]?.toUpperCase() ?? '';
    const n = u?.nom?.[0]?.toUpperCase() ?? '';
    return p + n || '?';
  }

  /** ✅ Mode sombre */
  get isDarkMode(): boolean {
    return this.themeService.isDarkMode();
  }

  /** ✅ Toggle du thème */
  toggleTheme(): void {
    this.themeService.toggleTheme();
  }
}
