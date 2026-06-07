import { Injectable, inject } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { ContratModel } from '../../models/contrats';
import { environment } from '../../../environments/environments';

@Injectable({
  providedIn: 'root',
})
export class ContratService {
  private http = inject(HttpClient);
  private apiUrl = `${environment.apiUrl}`;

  getContrats(employeId?: number): Observable<ContratModel[]> {
    let params = new HttpParams();
    if (employeId) {
      params = params.set('employe', employeId.toString());
    }
    return this.http.get<ContratModel[]>(`${this.apiUrl}/contrats/`, { params });
  }

  creerContrat(contrat: ContratModel): Observable<ContratModel> {
    return this.http.post<ContratModel>(`${this.apiUrl}/contrats/`, contrat);
  }

  modifierContrat(id: number, contrat: Partial<ContratModel>): Observable<ContratModel> {
    return this.http.put<ContratModel>(`${this.apiUrl}/contrats/${id}/`, contrat);
  }

  cloturerContrat(id: number): Observable<{ detail: string }> {
    return this.http.delete<{ detail: string }>(`${this.apiUrl}/contrats/${id}/`);
  }

  telechargerContratPDF(id: number, nomEmploye: string): void {
    this.http.get(`${this.apiUrl}/contrats/${id}/pdf/`, { responseType: 'blob' }).subscribe({
      next: (blob: Blob) => {
        const url = window.URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = `Contrat_${nomEmploye}.pdf`;
        link.click();
        window.URL.revokeObjectURL(url);
      },
      error: (err) => console.error('Erreur lors du téléchargement du PDF :', err),
    });
  }
}
