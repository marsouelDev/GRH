import { inject } from '@angular/core';
import { CanActivateFn, Router } from '@angular/router';
import { AuthService } from '../../services/auth/auth.service';

function redirectToLogin(router: Router): boolean {
  router.navigate(['/login']);
  return false;
}

export const authGuard: CanActivateFn = () => {
  const authService = inject(AuthService);
  const router = inject(Router);

  return authService.isLoggedIn() ? true : redirectToLogin(router);
};

export const adminGuard: CanActivateFn = () => {
  const authService = inject(AuthService);
  const router = inject(Router);

  return authService.isAdmin() ? true : redirectToLogin(router);
};

export const rhOrAdminGuard: CanActivateFn = () => {
  const authService = inject(AuthService);
  const router = inject(Router);

  return authService.isRH() || authService.isAdmin() ? true : redirectToLogin(router);
};

export const rhGuard: CanActivateFn = () => {
  const authService = inject(AuthService);
  const router = inject(Router);

  return authService.isRH() ? true : redirectToLogin(router);
};

export const employeGuard: CanActivateFn = () => {
  const authService = inject(AuthService);
  const router = inject(Router);

  return authService.isEmploye() ? true : redirectToLogin(router);
};
