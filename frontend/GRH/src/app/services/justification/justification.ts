import { Injectable, inject } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { Justification } from '../../models/justification';
import { environment } from '../../../environments/environments';

@Injectable({ providedIn: 'root' })
export class JustificationService {
  private readonly http = inject(HttpClient);
  private readonly apiUrl = `${environment.apiUrl}/justifications/`;

  getJustifications(filtres?: any): Observable<Justification[]> {
    let params = new HttpParams();
    if (filtres?.statut) params = params.set('statut', filtres.statut);
    if (filtres?.type_justif) params = params.set('type_justif', filtres.type_justif);
    if (filtres?.employe) params = params.set('employe', filtres.employe.toString());

    return this.http.get<Justification[]>(this.apiUrl, { params });
  }


  creerJustification(formData: FormData): Observable<any> {
    return this.http.post(this.apiUrl, formData);
  }

  valider(id: number, commentaire: string): Observable<any> {
    return this.http.put(`${this.apiUrl}${id}/valider/`, { commentaire });
  }

  rejeter(id: number, commentaire: string): Observable<any> {
    return this.http.put(`${this.apiUrl}${id}/rejeter/`, { commentaire });
  }

  supprimerJustification(id: number): Observable<any> {
    return this.http.delete(`${this.apiUrl}${id}/`);
  }
}