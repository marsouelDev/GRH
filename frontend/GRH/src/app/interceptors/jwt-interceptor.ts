import { HttpInterceptorFn, HttpErrorResponse } from '@angular/common/http';
import { inject } from '@angular/core';
import { Router } from '@angular/router';
import { HttpClient } from '@angular/common/http';
import { catchError, switchMap, throwError } from 'rxjs';
import { jwtDecode } from 'jwt-decode';

const REFRESH_URL = 'https://workflow-u1mk.onrender.com/api/refresh/';

// ───────────────── TYPES ─────────────────
interface JetonJwt {
  user_id?: number; //  AJOUTÉ
  role?: string;
  email?: string;
  nom?: string;
  prenom?: string;
  exp?: number;
}

// ───────────────── HELPERS ─────────────────
function getAccessToken(): string | null {
  return localStorage.getItem('access_token');
}

function getRefreshToken(): string | null {
  return localStorage.getItem('refresh_token');
}

function sauvegarderToken(access: string, refresh?: string): void {
  localStorage.setItem('access_token', access);
  if (refresh) {
    localStorage.setItem('refresh_token', refresh);
  }
  try {
    const decoded = jwtDecode<JetonJwt>(access);

    if (decoded.user_id) {
      localStorage.setItem('user_id', String(decoded.user_id));
    }

    localStorage.setItem('user_role', decoded.role || '');
    localStorage.setItem('user_email', decoded.email || '');
    localStorage.setItem('user_nom', decoded.nom || '');
    localStorage.setItem('user_prenom', decoded.prenom || '');
  } catch (error) {
  }
}

function deconnecterEtRediriger(router: Router): void {
  localStorage.removeItem('access_token');
  localStorage.removeItem('refresh_token');
  localStorage.removeItem('user_id'); 
  localStorage.removeItem('user_role');
  localStorage.removeItem('user_email');
  localStorage.removeItem('user_nom');
  localStorage.removeItem('user_prenom');
  router.navigate(['/login']);
}

// ───────────────── INTERCEPTEUR ─────────────────
export const jwtInterceptor: HttpInterceptorFn = (req, next) => {
  const router = inject(Router);
  const http = inject(HttpClient);

  const estPublique =
    req.url.includes('/login/') || req.url.includes('/refresh/') || req.url.includes('/logout/');

  // Attache le token sur toutes les requêtes privées
  const token = getAccessToken();
  if (token && !estPublique) {
    req = req.clone({
      setHeaders: { Authorization: `Bearer ${token}` },
    });
  }

  return next(req).pipe(
    catchError((error: HttpErrorResponse) => {
      // Token expiré → tenter un refresh
      if (error.status === 401 && !req.url.includes('/refresh/')) {
        const refreshToken = getRefreshToken();

        if (!refreshToken) {
          deconnecterEtRediriger(router);
          return throwError(() => error);
        }

        return http.post<any>(REFRESH_URL, { refresh: refreshToken }).pipe(
          switchMap((data) => {
            //  Décode et sauvegarde le nouveau token + user_id
            sauvegarderToken(data.access, data.refresh);

            const requeteRelancee = req.clone({
              setHeaders: { Authorization: `Bearer ${data.access}` },
            });

            return next(requeteRelancee);
          }),
          catchError((erreurRefresh) => {
            deconnecterEtRediriger(router);
            return throwError(() => erreurRefresh);
          }),
        );
      }

      return throwError(() => error);
    }),
  );
};
