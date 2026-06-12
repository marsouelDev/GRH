import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { EmployesStats, DashboardStats } from '../../models/analytics';

@Injectable({
  providedIn: 'root',
})
export class Dashboard {
  private http = inject(HttpClient);
  private apiUrl = 'https://workflow-u1mk.onrender.com';

  /** Récupère toutes les stats du dashboard RH/Admin */
  getDashboardStats(): Observable<DashboardStats> {
    return this.http.get<DashboardStats>(`${this.apiUrl}/dashboard/`);
  }

  /** Récupère les stats détaillées des employés */
  getEmployesStats(): Observable<EmployesStats> {
    return this.http.get<EmployesStats>(`${this.apiUrl}/dashboard/employes/`);
  }

  /** Récupère les stats personnelles d'un employé (dashboard employé) */
  getEmployeStats(employeId: number): Observable<any> {
    return this.http.get(`${this.apiUrl}/dashboard/employe/${employeId}/`);
  }
}
