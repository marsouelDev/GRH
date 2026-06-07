// src/app/services/conges/conges.service.ts

import { Injectable, inject } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { CongeModel } from '../../models/conge';
import { environment } from '../../../environments/environments';

@Injectable({ providedIn: 'root' })
export class CongeService {
  private readonly http = inject(HttpClient);
  
  private readonly apiUrl = `${environment.apiUrl}/conges/`;

  getConges(filtres?: any): Observable<CongeModel[]> {
    let params = new HttpParams();
    if (filtres?.statut) params = params.set('statut', filtres.statut);
    if (filtres?.employeId) params = params.set('employe', filtres.employeId.toString());
    
    
    return this.http.get<CongeModel[]>(this.apiUrl, { params });
  }

  getConge(id: number): Observable<CongeModel> {
    return this.http.get<CongeModel>(`${this.apiUrl}${id}/`);
  }

  creerConge(data: Partial<CongeModel>): Observable<any> {
    return this.http.post(this.apiUrl, data);
  }

  modifierConge(id: number, data: Partial<CongeModel>): Observable<any> {
    return this.http.patch(`${this.apiUrl}${id}/`, data);
  }

  annulerConge(id: number): Observable<any> {
    return this.http.delete(`${this.apiUrl}${id}/`);
  }

  approuverConge(id: number, commentaire: string = ''): Observable<any> {
    return this.http.put(`${this.apiUrl}${id}/approuver/`, { commentaire });
  }

  refuserConge(id: number, data: { commentaire: string }): Observable<any> {
    return this.http.put(`${this.apiUrl}${id}/refuser/`, data);
  }
}