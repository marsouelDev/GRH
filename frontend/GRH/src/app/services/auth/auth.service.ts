import { Injectable, inject } from '@angular/core';
import { Router } from '@angular/router';
import { HttpClient } from '@angular/common/http';
import { Observable, tap } from 'rxjs';
import { jwtDecode } from 'jwt-decode';

// ───────────────── TYPES ─────────────────
interface JetonJwt {
  user_id?: number;
  role?: string;
  email?: string;
  nom?: string;
  prenom?: string;
  exp?: number;
}

export interface UtilisateurCourant {
  id: number | undefined;
  email: string;
  nom: string;
  prenom: string;
  role: string;
}

const CLE = {
  ACCESS: 'access_token',
  REFRESH: 'refresh_token',
  USER_ID: 'user_id',
  ROLE: 'user_role',
  EMAIL: 'user_email',
  NOM: 'user_nom',
  PRENOM: 'user_prenom',
} as const;

@Injectable({
  providedIn: 'root',
})
export class AuthService {
  private readonly apiUrl = 'http://localhost:8000/api';
  private router = inject(Router);
  private http = inject(HttpClient);

  // ───────────────── LOGIN & LOGOUT ─────────────────

  login(donneesConnexion: any): Observable<any> {
    return this.http.post<any>(`${this.apiUrl}/login/`, donneesConnexion).pipe(
      tap((reponse) => {
        if (reponse?.access) {
          this.nettoyerSessionLocale(false);
          this.saveToken(reponse.access, reponse.refresh);
        }
      }),
    );
  }

  logout(): void {
    const refreshToken = this.getRefreshToken();
    if (refreshToken) {
      this.http.post(`${this.apiUrl}/logout/`, { refresh: refreshToken }).subscribe({
        next: () => this.nettoyerSessionLocale(),
        error: () => this.nettoyerSessionLocale(),
      });
    } else {
      this.nettoyerSessionLocale();
    }
  }

  // ───────────────── GESTION DES TOKENS ─────────────────

  saveToken(access: string, refresh?: string): void {
    localStorage.setItem(CLE.ACCESS, access);
    if (refresh) {
      localStorage.setItem(CLE.REFRESH, refresh);
    }

    try {
      const decoded = jwtDecode<JetonJwt>(access);

      //  Stocker l'ID utilisateur
      if (decoded.user_id) {
        localStorage.setItem(CLE.USER_ID, String(decoded.user_id));
      }

      localStorage.setItem(CLE.ROLE, decoded.role || 'EMPLOYE');
      localStorage.setItem(CLE.EMAIL, decoded.email || '');
      localStorage.setItem(CLE.NOM, decoded.nom || '');
      localStorage.setItem(CLE.PRENOM, decoded.prenom || '');
    } catch (error) {
      localStorage.setItem(CLE.ROLE, 'EMPLOYE');
    }
  }

  getToken(): string | null {
    return localStorage.getItem(CLE.ACCESS);
  }

  getRefreshToken(): string | null {
    return localStorage.getItem(CLE.REFRESH);
  }

  // ───────────────── ROLES ─────────────────

  getRole(): string {
    return localStorage.getItem(CLE.ROLE) || 'EMPLOYE';
  }

  isAdmin(): boolean {
    return this.getRole() === 'ADMIN';
  }

  isRH(): boolean {
    return this.getRole() === 'RH';
  }

  isEmploye(): boolean {
    return this.getRole() === 'EMPLOYE';
  }

  hasRole(roles: string[]): boolean {
    return roles.includes(this.getRole());
  }

  // ───────────────── UTILISATEUR & ÉTAT ─────────────────

  isLoggedIn(): boolean {
    return !!this.getToken();
  }

  getCurrentUser(): UtilisateurCourant {
    const userId = localStorage.getItem(CLE.USER_ID);
    return {
      id: userId ? Number(userId) : undefined,
      email: localStorage.getItem(CLE.EMAIL) || '',
      nom: localStorage.getItem(CLE.NOM) || '',
      prenom: localStorage.getItem(CLE.PRENOM) || '',
      role: this.getRole(),
    };
  }

  // ───────────────── NAVIGATION ─────────────────

  redirectByRole(): void {
    const role = this.getRole();
    switch (role) {
      case 'ADMIN':
        this.router.navigate(['/admin/dashboard-admin']);
        break;
      case 'RH':
        this.router.navigate(['/rh/dashboard-rh']);
        break;
      case 'EMPLOYE':
        this.router.navigate(['/employe/dashboard-employe']);
        break;
      default:
        this.router.navigate(['/login']);
    }
  }

  private nettoyerSessionLocale(redirect = true): void {
    localStorage.clear();
    if (redirect) {
      this.router.navigate(['/login']);
    }
  }
}
