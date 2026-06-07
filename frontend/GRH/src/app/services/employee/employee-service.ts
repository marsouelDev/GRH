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


  createEmploye(employe: EmployeModels): Observable<any> {
    return this.http.post<any>(`${this.apiUrl}/`, employe, this.getOptions());
  }

 
  updateEmploye(id: number, employe: Partial<EmployeModels>): Observable<EmployeModels> {
    return this.http.put<EmployeModels>(`${this.apiUrl}/${id}/`, employe, this.getOptions());
  }


  deleteEmploye(id: number): Observable<{ detail: string }> {
    return this.http.delete<{ detail: string }>(`${this.apiUrl}/${id}/`, this.getOptions());
  }


  activeEmploye(id: number): Observable<any> {
    return this.http.put<any>(`${this.apiUrl}/${id}/active/`, {}, this.getOptions());
  }

 
  updateProfil(
    id: number,
    donnéesProfil: Partial<EmployeModels> & { password?: string },
  ): Observable<EmployeModels> {
    return this.http.put<EmployeModels>(
      `${this.apiUrl}/${id}/profil/`,
      donnéesProfil,
      this.getOptions(),
    );
  }
}
