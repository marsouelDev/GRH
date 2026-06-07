// src/app/services/rh/rh.service.ts
import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../../environments/environments';
import { RHModel } from '../../models/rh';

@Injectable({ providedIn: 'root' })
export class RhService {
  private readonly http = inject(HttpClient);
  private readonly apiUrl = `${environment.apiUrl}/RH/`;

  /** GET /RH/ — Liste de tous les RH */
  getRhs(): Observable<RHModel[]> {
    return this.http.get<RHModel[]>(this.apiUrl);
  }

  /** GET /RH/<pk>/ — Détail d'un RH */
  getRh(id: number): Observable<RHModel> {
    return this.http.get<RHModel>(`${this.apiUrl}${id}/`);
  }

  /** POST /RH/ — Créer un nouveau RH */
  creerRh(data: Partial<RHModel>): Observable<RHModel & { notification?: string }> {
    return this.http.post<RHModel & { notification?: string }>(this.apiUrl, data);
  }

  /** PUT /RH/<pk>/ — Modifier un RH (Admin + RH) */
  modifierRh(id: number, data: Partial<RHModel>): Observable<RHModel> {
    return this.http.put<RHModel>(`${this.apiUrl}${id}/`, data);
  }

  /** DELETE /RH/<pk>/ — Désactiver un RH (Admin uniquement) */
  desactiverRh(id: number): Observable<{ detail: string }> {
    return this.http.delete<{ detail: string }>(`${this.apiUrl}${id}/`);
  }

  /** PUT /RH/<pk>/activer/ — Réactiver un RH (Admin uniquement) */
  activerRh(id: number): Observable<{ detail: string; RH: RHModel }> {
    return this.http.put<{ detail: string; RH: RHModel }>(`${this.apiUrl}${id}/activer/`, {});
  }

  /** PUT /RH/<pk>/profil/ — Modifier son propre profil */
  modifierProfil(id: number, data: Partial<RHModel>): Observable<RHModel> {
    return this.http.put<RHModel>(`${this.apiUrl}${id}/profil/`, data);
  }
}
