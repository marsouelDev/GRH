// src/app/services/presence/presence.service.ts

import { Injectable, inject } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { Presence } from '../../models/presences';
import { environment } from '../../../environments/environments'; 

@Injectable({ providedIn: 'root' })
export class PresenceService {
  private readonly http = inject(HttpClient);

 
  private readonly apiUrl = `${environment.apiUrl}/presences`;

  
  getPresences(employeId?: number): Observable<Presence[]> {
    let params = new HttpParams();

    if (employeId) {
      params = params.set('employe', employeId.toString());
    }

    return this.http.get<Presence[]>(this.apiUrl, { params });
  }

  badgerArrivee(): Observable<Presence> {
    return this.http.post<Presence>(`${this.apiUrl}/arrivee/`, {});
  }

  badgerDepart(): Observable<Presence> {
    return this.http.post<Presence>(`${this.apiUrl}/depart/`, {});
  }
}
