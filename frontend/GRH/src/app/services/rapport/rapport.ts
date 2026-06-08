import { Injectable, inject } from '@angular/core';
import { HttpClient, HttpHeaders, HttpParams, HttpErrorResponse } from '@angular/common/http';
import { Observable, throwError } from 'rxjs';
import { catchError } from 'rxjs/operators';
import { RapportModel } from '../../models/rapport';
import { environment } from '../../../environments/environments';

@Injectable({ providedIn: 'root' })
export class RapportService {
  private http = inject(HttpClient);
  private readonly apiUrl = `${environment.apiUrl}/rapports`;

  constructor() {}

  private getHeaders(): HttpHeaders {
    const token = localStorage.getItem('access_token') || '';
    return new HttpHeaders()
      .set('Authorization', `Bearer ${token}`)
      .set('Content-Type', 'application/json');
  }

  private handleError(error: HttpErrorResponse) {
    const message = error.error?.detail || error.error?.message || 'Une erreur est survenue';
    console.error('Erreur API:', error);
    return throwError(() => new Error(message));
  }

  getRapports(typeRapport?: string): Observable<RapportModel[]> {
    let params = new HttpParams();
    if (typeRapport) params = params.set('type', typeRapport);
    return this.http
      .get<RapportModel[]>(`${this.apiUrl}/`, { headers: this.getHeaders(), params })
      .pipe(catchError(this.handleError));
  }

  getRapport(id: number): Observable<RapportModel> {
    return this.http
      .get<RapportModel>(`${this.apiUrl}/${id}/`, { headers: this.getHeaders() })
      .pipe(catchError(this.handleError));
  }

  creerRapport(data: Partial<RapportModel>): Observable<RapportModel> {
    return this.http
      .post<RapportModel>(`${this.apiUrl}/`, data, { headers: this.getHeaders() })
      .pipe(catchError(this.handleError));
  }

  regenerer(id: number): Observable<RapportModel> {
    return this.http
      .put<RapportModel>(`${this.apiUrl}/${id}/regenerer/`, {}, { headers: this.getHeaders() })
      .pipe(catchError(this.handleError));
  }

  supprimer(id: number): Observable<any> {
    return this.http
      .delete(`${this.apiUrl}/${id}/`, { headers: this.getHeaders() })
      .pipe(catchError(this.handleError));
  }

 exporterExcel(id: number): Observable<Blob> {
    return this.http.get(`${this.apiUrl}/${id}/export/excel/`, { 
      responseType: 'blob' 
    });
  }

  exporterPdf(id: number): Observable<Blob> {
    return this.http.get(`${this.apiUrl}/${id}/export/pdf/`, { 
      responseType: 'blob' 
    });
  }
}
