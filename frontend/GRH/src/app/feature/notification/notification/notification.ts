import {
  Component,
  OnInit,
  OnDestroy,
  ChangeDetectorRef,
  ChangeDetectionStrategy,
} from '@angular/core';
import { CommonModule, DatePipe } from '@angular/common';
import { RouterLink } from '@angular/router';
import { Subscription } from 'rxjs';
import { NotificationService } from '../../../services/notification/notification-services';
import { Notification as AppNotification } from '../../../models/notification';

@Component({
  selector: 'app-notifications',
  standalone: true,
  imports: [CommonModule, RouterLink, DatePipe],
  templateUrl: './notification.html',
  styleUrl: './notification.css',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class NotificationsComponent implements OnInit, OnDestroy {
  notifications: AppNotification[] = [];
  filtreActuel: 'all' | 'true' | 'false' = 'all';
  chargement = false;
  nonLuesCount = 0;

  private subscriptions: Subscription[] = [];

  constructor(
    private notifService: NotificationService,
    private cdr: ChangeDetectorRef,
  ) {}

  ngOnInit(): void {
    this.chargerNotifications();

    const sub = this.notifService.getNonLuesCount().subscribe((count) => {
      this.nonLuesCount = count;
      this.cdr.markForCheck();
    });
    this.subscriptions.push(sub);
  }

  ngOnDestroy(): void {
    this.subscriptions.forEach((s) => s.unsubscribe());
  }

  chargerNotifications(): void {
    this.chargement = true;
    this.cdr.markForCheck();

    const paramFiltre = this.filtreActuel === 'all' ? undefined : this.filtreActuel;

    this.notifService.getNotifications(paramFiltre).subscribe({
      next: (data: AppNotification[]) => {
        this.notifications = data;
        this.chargement = false;
        this.cdr.markForCheck();
      },
      error: (err: any) => {
        console.error(' Erreur chargement notifications:', err);
        this.chargement = false;
        this.cdr.markForCheck();
      },
    });
  }

  changerFiltre(nouveauFiltre: 'all' | 'true' | 'false'): void {
    if (this.filtreActuel === nouveauFiltre) return;
    this.filtreActuel = nouveauFiltre;
    this.chargerNotifications();
  }

  lireUne(id: number): void {
    this.notifService.marquerCommeLue(id).subscribe({
      next: () => {
        this.notifications = this.notifications.map((n) => (n.id === id ? { ...n, lu: true } : n));
        this.cdr.markForCheck();
      },
      error: (err: any) => {
        console.error(' Erreur marquage notification:', err);
      },
    });
  }

  toutLire(): void {
    if (this.notifications.every((n) => n.lu)) return;

    this.notifService.toutMarquerCommeLu().subscribe({
      next: () => {
        this.notifications = this.notifications.map((n) => ({ ...n, lu: true }));
        this.cdr.markForCheck();
      },
      error: (err: any) => {
        console.error(' Erreur marquage global:', err);
      },
    });
  }

  getBadgeClass(typeNotif: string): string {
    const classes: Record<string, string> = {
      CONGE_SOUMIS: 'badge-conge-soumis',
      CONGE_APPROUVE: 'badge-conge-approuve',
      CONGE_REFUSE: 'badge-conge-refuse',
      JUSTIF_SOUMISE: 'badge-justif-soumise',
      JUSTIF_VALIDEE: 'badge-justif-validee',
      JUSTIF_REJETEE: 'badge-justif-rejetee',
      ANNIVERSAIRE: 'badge-anniversaire',
      RAPPEL: 'badge-rappel',
      SYSTEME: 'badge-systeme',
    };
    return classes[typeNotif] || 'badge-default';
  }

  asDate(dateString: string): Date {
    return new Date(dateString);
  }

  trackById(index: number, item: AppNotification): number {
    return item.id;
  }
}
