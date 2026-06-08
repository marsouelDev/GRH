// src/app/services/notification/notification.service.ts

import { Injectable, inject } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable, BehaviorSubject, tap } from 'rxjs';
import { Notification } from '../../models/notification';
import { environment } from '../../../environments/environments';

@Injectable({ providedIn: 'root' })
export class NotificationService {
  private readonly http = inject(HttpClient);
  private readonly apiUrl = `${environment.apiUrl}/notifications/`;

  private nonLuesCountSubject = new BehaviorSubject<number>(0);
  nonLuesCount$ = this.nonLuesCountSubject.asObservable();

  mettreAJourCompteur(notifications: Notification[]): void {
    const totalNonLues = notifications.filter((n) => !n.lu).length;
    this.nonLuesCountSubject.next(totalNonLues);
  }

  getNotifications(lu?: 'true' | 'false'): Observable<Notification[]> {
    let params = new HttpParams();
    if (lu) params = params.set('lu', lu);

    return this.http.get<Notification[]>(this.apiUrl, { params }).pipe(
      tap((notifs) => {
        if (!lu) this.mettreAJourCompteur(notifs);
      }),
    );
  }

  marquerCommeLue(id: number): Observable<{ detail: string }> {
    return this.http.put<{ detail: string }>(`${this.apiUrl}${id}/lire/`, {}).pipe(
      tap(() => {
        const current = this.nonLuesCountSubject.value;
        if (current > 0) this.nonLuesCountSubject.next(current - 1);
      }),
    );
  }

  toutMarquerCommeLu(): Observable<{ detail: string }> {
    return this.http
      .put<{ detail: string }>(`${this.apiUrl}tout-lire/`, {})
      .pipe(tap(() => this.nonLuesCountSubject.next(0)));
  }

  getNonLuesCount(): Observable<number> {
    return this.nonLuesCount$;
  }
}
