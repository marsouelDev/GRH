// layout.service.ts
import { Injectable, signal } from '@angular/core';
import { BehaviorSubject } from 'rxjs';

@Injectable({ providedIn: 'root' })
export class LayoutService {
  private sidebarOpenSubject = new BehaviorSubject<boolean>(false);
  sidebarOpen$ = this.sidebarOpenSubject.asObservable();

  sidebarOpen = signal(false);

  toggleSidebar(): void {
    const newState = !this.sidebarOpen();
    this.sidebarOpen.set(newState);
    this.sidebarOpenSubject.next(newState);
  }

  closeSidebar(): void {
    this.sidebarOpen.set(false);
    this.sidebarOpenSubject.next(false);
  }

  openSidebar(): void {
    this.sidebarOpen.set(true);
    this.sidebarOpenSubject.next(true);
  }
}
