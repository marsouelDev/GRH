import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable } from 'rxjs';
import { EmployeModels } from '../../models/employe';

@Injectable({
  providedIn: 'root',
})
export class EmployeeService {
  private apiUrl = 'http://localhost:8000/employes';

  constructor(private http: HttpClient) {}

  private getOptions(): { headers: HttpHeaders } {
    const token = localStorage.getItem('access_token') || '';
    const headers = new HttpHeaders()
      .set('Authorization', `Bearer ${token}`)
      .set('Content-Type', 'application/json');
    return { headers };
  }

  getEmployes(): Observable<EmployeModels[]> {
    return this.http.get<EmployeModels[]>(`${this.apiUrl}/`, this.getOptions());
  }

  getEmploye(id: number): Observable<EmployeModels> {
    return this.http.get<EmployeModels>(`${this.apiUrl}/${id}/`, this.getOptions());
  }

  // CORRECTION : retour typé en 'any' pour récupérer le champ 'notification'
  // renvoyé par le backend en plus des champs de EmployeModels
  createEmploye(employe: EmployeModels): Observable<any> {
    return this.http.post<any>(`${this.apiUrl}/`, employe, this.getOptions());
  }

  updateEmploye(id: number, employe: Partial<EmployeModels>): Observable<EmployeModels> {
    return this.http.put<EmployeModels>(`${this.apiUrl}/${id}/`, employe, this.getOptions());
  }

  deleteEmploye(id: number): Observable<{ detail: string }> {
    return this.http.delete<{ detail: string }>(`${this.apiUrl}/${id}/`, this.getOptions());
  }
  
}
