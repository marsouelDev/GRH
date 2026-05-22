import { HttpInterceptorFn, HttpErrorResponse } from '@angular/common/http';
import { inject } from '@angular/core';
import { Router } from '@angular/router';
import { HttpClient } from '@angular/common/http';
import { catchError, switchMap, throwError } from 'rxjs';

export const jwtInterceptor: HttpInterceptorFn = (req, next) => {
  const router = inject(Router);
  const http = inject(HttpClient);

  // Ajoute le token sur toutes les requêtes sauf le login et le refresh
  const token = localStorage.getItem('access_token');
  if (token && !req.url.includes('/login/') && !req.url.includes('/refresh/')) {
    req = req.clone({
      setHeaders: { Authorization: `Bearer ${token}` },
    });
  }

  return next(req).pipe(
    catchError((error: HttpErrorResponse) => {
      // Si 401 et que ce n'est pas déjà une requête de refresh
      if (error.status === 401 && !req.url.includes('/refresh/')) {
        const refreshToken = localStorage.getItem('refresh_token');

        if (!refreshToken) {
          localStorage.clear();
          router.navigate(['/login']);
          return throwError(() => error);
        }

        // Tente de renouveler le token
        return http
          .post<any>('http://localhost:8000/api/refresh/', {
            refresh: refreshToken,
          })
          .pipe(
            switchMap((data) => {
              // Sauvegarde le nouveau access token
              localStorage.setItem('access_token', data.access);

              // Rejoue la requête originale avec le nouveau token
              const retryReq = req.clone({
                setHeaders: { Authorization: `Bearer ${data.access}` },
              });
              return next(retryReq);
            }),
            catchError((refreshError) => {
              // Refresh échoué (refresh token expiré) → déconnexion
              localStorage.clear();
              router.navigate(['/login']);
              return throwError(() => refreshError);
            }),
          );
      }

      return throwError(() => error);
    }),
  );
};
