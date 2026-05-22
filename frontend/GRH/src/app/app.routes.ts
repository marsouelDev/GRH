import { Routes } from '@angular/router';
import { Login } from './components/login/login';
import { PageNotFound } from './components/page-not-found/page-not-found';
import { authGuard, rhOrAdminGuard } from '../app/services/authGuard/auth.guard';
import { Employee } from './components/employee/employee/employee';

export const routes: Routes = [
  { path: 'login', component: Login },
  { path: 'page', component: PageNotFound },
  { path: 'employees', component: Employee, canActivate: [rhOrAdminGuard] },
  { path: 'employees/create', component: Employee, canActivate: [rhOrAdminGuard] },
  { path: 'employees/edit/:id', component: Employee, canActivate: [rhOrAdminGuard] },
];
