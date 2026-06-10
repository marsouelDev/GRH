import { Injectable, inject } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable, throwError } from 'rxjs';
import { catchError } from 'rxjs/operators';
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

    return this.http.get<CongeModel[]>(this.apiUrl, { params }).pipe(
      catchError((err) => {
        console.error('❌ Erreur getConges:', err);
        return throwError(() => err);
      }),
    );
  }

  getConge(id: number): Observable<CongeModel> {
    return this.http.get<CongeModel>(`${this.apiUrl}${id}/`).pipe(
      catchError((err) => {
        console.error('❌ Erreur getConge:', err);
        return throwError(() => err);
      }),
    );
  }

  creerConge(data: Partial<CongeModel>): Observable<any> {
    console.log('📤 Créer congé:', data);
    return this.http.post(this.apiUrl, data).pipe(
      catchError((err) => {
        console.error('❌ Erreur creerConge:', err);
        return throwError(() => err);
      }),
    );
  }

  modifierConge(id: number, data: Partial<CongeModel>): Observable<any> {
    console.log('📤 Modifier congé:', id, data);
    return this.http.patch(`${this.apiUrl}${id}/`, data).pipe(
      catchError((err) => {
        console.error('❌ Erreur modifierConge:', err);
        return throwError(() => err);
      }),
    );
  }

  annulerConge(id: number): Observable<any> {
    console.log('📤 Annuler congé:', id);
    return this.http.delete(`${this.apiUrl}${id}/`).pipe(
      catchError((err) => {
        console.error('❌ Erreur annulerConge:', err);
        return throwError(() => err);
      }),
    );
  }

  approuverConge(id: number, commentaire: string = ''): Observable<any> {
    console.log('📤 Approuver congé:', id, { commentaire });
    return this.http.put(`${this.apiUrl}${id}/approuver/`, { commentaire }).pipe(
      catchError((err) => {
        console.error('❌ Erreur approuverConge:', err);
        return throwError(() => err);
      }),
    );
  }

  refuserConge(id: number, data: { commentaire: string }): Observable<any> {
    console.log('📤 Refuser congé:', id, data);
    return this.http.put(`${this.apiUrl}${id}/refuser/`, data).pipe(
      catchError((err) => {
        console.error('❌ Erreur refuserConge:', err);
        return throwError(() => err);
      }),
    );
  }
}
