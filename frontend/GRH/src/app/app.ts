import { Component, signal } from '@angular/core';
import { Router, RouterOutlet, NavigationEnd } from '@angular/router';
import { CommonModule } from '@angular/common';
import { NavBar } from './shared/nav-bar/nav-bar';
import { SideBar } from './shared//side-bar/side-bar';
import { AuthService } from './services/auth/auth.service';
import { filter } from 'rxjs/operators';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [RouterOutlet, CommonModule, NavBar, SideBar],
  templateUrl: './app.html',
  styleUrl: './app.css',
})
export class App {
  protected readonly title = signal('GRH');
  afficherLayout = false;

  constructor(
    private authService: AuthService,
    private router: Router,
  ) {
    this.router.events.pipe(filter((e) => e instanceof NavigationEnd)).subscribe((e: any) => {
      const urlsSansLayout = ['/login', '/page'];
      const estPageSansLayout = urlsSansLayout.some((u) => e.url.startsWith(u));
      this.afficherLayout = !estPageSansLayout && this.authService.isLoggedIn();
    });
  }
}
