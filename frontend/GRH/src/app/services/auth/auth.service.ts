import { Injectable } from '@angular/core';
import { Router } from '@angular/router';
import { HttpClient } from '@angular/common/http'; // Ajouté pour les requêtes API
import { Observable, tap } from 'rxjs'; // Ajouté pour gérer le flux de données
import { jwtDecode } from 'jwt-decode';

interface jetonJwt {
  role?: string;
  email?: string;
  nom?: string;
  prenom?: string;
  exp?: number;
}

@Injectable({
  providedIn: 'root',
})
export class AuthService {
  private apiUrl = 'http://localhost:8000/api';

  // Injection de HttpClient dans le constructeur
  constructor(
    private router: Router,
    private http: HttpClient,
  ) {}

  login(donneesConnexion: any): Observable<any> {
    return this.http.post<any>(`${this.apiUrl}/login/`, donneesConnexion).pipe(
      tap((reponse) => {
        if (reponse && reponse.access) {
          // Sauvegarde de l'access et du refresh token
          this.saveToken(reponse.access, reponse.refresh);
        }
      }),
    );
  }
  // ── Sauvegarder le token et le refresh token
  saveToken(access: string, refresh?: string): void {
    localStorage.setItem('access_token', access);
    if (refresh) {
      localStorage.setItem('refresh_token', refresh);
    }

    try {
      const decoded = jwtDecode<jetonJwt>(access);
      localStorage.setItem('user_role', decoded.role || 'EMPLOYE');
      localStorage.setItem('user_email', decoded.email || '');
      localStorage.setItem('user_nom', decoded.nom || '');
      localStorage.setItem('user_prenom', decoded.prenom || '');
    } catch {
      localStorage.setItem('user_role', 'EMPLOYE');
    }
  }

  getToken(): string | null {
    return localStorage.getItem('access_token');
  }

  getRefreshToken(): string | null {
    return localStorage.getItem('refresh_token');
  }

  isLoggedIn(): boolean {
    const token = this.getToken();
    if (!token) return false;
    try {
      const decoded = jwtDecode<jetonJwt>(token);
      const now = Math.floor(Date.now() / 1000);
      return decoded.exp ? decoded.exp > now : true;
    } catch {
      return false;
    }
  }

  getRole(): string {
    return localStorage.getItem('user_role') || 'EMPLOYE';
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

  getCurrentUser(): { email: string; nom: string; prenom: string; role: string } {
    return {
      email: localStorage.getItem('user_email') || '',
      nom: localStorage.getItem('user_nom') || '',
      prenom: localStorage.getItem('user_prenom') || '',
      role: this.getRole(),
    };
  }

  // ── Déconnexion Complète (Backend + Frontend activé) ──
  logout(): void {
    const refreshToken = this.getRefreshToken();

    if (refreshToken) {
      // Envoie le refresh token au backend pour le blacklister
      this.http.post(`${this.apiUrl}/logout/`, { refresh: refreshToken }).subscribe({
        next: () => this.nettoyerSessionLocale(),
        error: () => this.nettoyerSessionLocale(), 
      });
    } else {
      this.nettoyerSessionLocale();
    }
  }

  // Supprime les données du navigateur et redirige
  private nettoyerSessionLocale(): void {
    localStorage.clear();
    this.router.navigate(['/login']);
  }
}
