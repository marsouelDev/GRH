import { Injectable, inject } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { PosteModel } from '../../models/poste';
import { environment } from '../../../environments/environments';

@Injectable({
  providedIn: 'root',
})
export class PosteService {
  private http = inject(HttpClient);
  private apiUrl = `${environment.apiUrl}`;

  getPostes(inclureArchives: boolean = false): Observable<PosteModel[]> {
    let params = new HttpParams();
    if (inclureArchives) {
      params = params.set('actif', 'all');
    }
    return this.http.get<PosteModel[]>(`${this.apiUrl}/postes/`, { params });
  }

  getPoste(id: number): Observable<PosteModel> {
    return this.http.get<PosteModel>(`${this.apiUrl}/postes/${id}/`);
  }

  creerPoste(poste: PosteModel): Observable<PosteModel> {
    return this.http.post<PosteModel>(`${this.apiUrl}/postes/`, poste);
  }

  modifierPoste(id: number, poste: Partial<PosteModel>): Observable<PosteModel> {
    return this.http.put<PosteModel>(`${this.apiUrl}/postes/${id}/`, poste);
  }

  archiverPoste(id: number): Observable<{ detail: string }> {
    return this.http.delete<{ detail: string }>(`${this.apiUrl}/postes/${id}/`);
  }

  reactiverPoste(id: number): Observable<{ detail: string; poste: PosteModel }> {
    return this.http.put<{ detail: string; poste: PosteModel }>(
      `${this.apiUrl}/postes/${id}/activer/`,
      {},
    );
  }
}
