import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders, HttpErrorResponse } from '@angular/common/http';
import { Observable, throwError } from 'rxjs';
import { catchError, map } from 'rxjs/operators';
import { AdministrateursModels } from '../../models/administrateur';
import { environment } from '../../../environments/environments';

@Injectable({
  providedIn: 'root',
})
export class AdministrateurService {
  private readonly apiUrl = `${environment.apiUrl}/administrateurs`;

  constructor(private http: HttpClient) {}

  private getHeaders(): HttpHeaders {
    const token = localStorage.getItem('access_token') || '';
    return new HttpHeaders()
      .set('Authorization', `Bearer ${token}`)
      .set('Content-Type', 'application/json');
  }

  private handleError(error: HttpErrorResponse) {
    console.error('Erreur API:', error);
    const message = error.error?.detail || error.message || 'Une erreur est survenue';
    return throwError(() => new Error(message));
  }

  getAdministrateurs(): Observable<AdministrateursModels[]> {
    return this.http.get<any>(`${this.apiUrl}/`, { headers: this.getHeaders() }).pipe(
      map((response) => {
        if (response && Array.isArray(response.results)) {
          return response.results;
        }
        if (Array.isArray(response)) {
          return response;
        }
        return [];
      }),
      catchError(this.handleError),
    );
  }

  getAdministrateur(id: number): Observable<AdministrateursModels> {
    return this.http
      .get<AdministrateursModels>(`${this.apiUrl}/${id}/`, { headers: this.getHeaders() })
      .pipe(catchError(this.handleError));
  }

  createAdministrateur(admin: AdministrateursModels): Observable<any> {
    return this.http
      .post<any>(`${this.apiUrl}/`, admin, { headers: this.getHeaders() })
      .pipe(catchError(this.handleError));
  }

  updateAdministrateur(
    id: number,
    admin: Partial<AdministrateursModels>,
  ): Observable<AdministrateursModels> {
    return this.http
      .put<AdministrateursModels>(`${this.apiUrl}/${id}/`, admin, { headers: this.getHeaders() })
      .pipe(catchError(this.handleError));
  }

  updateProfil(
    id: number,
    donnéesProfil: Partial<AdministrateursModels> & { password?: string },
  ): Observable<AdministrateursModels> {
    return this.http
      .put<AdministrateursModels>(`${this.apiUrl}/${id}/profil/`, donnéesProfil, {
        headers: this.getHeaders(),
      })
      .pipe(catchError(this.handleError));
  }
}
