import { Component, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterOutlet } from '@angular/router';
import { toSignal } from '@angular/core/rxjs-interop';

import { Sidebar } from '../sidebar/sidebar';
import { Navbar } from '../navbar/navbar';
import { ThemeService } from '../../services/Theme/theme-service';
import { LayoutService } from '../../services/layoutService/layout.service';

@Component({
  selector: 'app-main-layouts',
  standalone: true,
  imports: [CommonModule, Sidebar, Navbar, RouterOutlet],
  templateUrl: './main-layouts.html',
  styleUrl: './main-layouts.css',
})
export class MainLayouts {
  theme = inject(ThemeService);
  layoutService = inject(LayoutService);

  // Converti en signal pour le template — pas de subscription manuelle
  isSidebarOpen = toSignal(this.layoutService.sidebarOpen$, { initialValue: false });

  toggleSidebar(): void {
    this.layoutService.toggleSidebar();
  }
  closeSidebar(): void {
    this.layoutService.closeSidebar();
  }
}
