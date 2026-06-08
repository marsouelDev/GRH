import { Routes } from '@angular/router';

import { Login } from './components/login/login';
import { MainLayouts } from './layouts/main-layouts/main-layouts';
import { PageNotFound } from './components/page-not-found/page-not-found';

import { DashboardAdmin } from './pages/admin/dashboard-admin/dashboard-admin';
import { DashboardRh } from './pages/rh/dashboard-rh/dashboard-rh';
import { DashboardEmploye } from './pages/employe/dashboard-employe/dashboard-employe';

import { Employee } from './components/employee/employee/employee';
import { PresenceListComponent } from './feature/presence/presence';
import { CongeComponent } from '../app/feature/conges/conges/conges';
import { NotificationsComponent } from './feature/notification/notification/notification';
import { ContratsComponent } from './feature/contrats/contrats/contrats';
import { PostesComponent } from './feature/poste/poste/poste';
import { JustificationComponent } from './feature/justification/justification/justification';
import { AdministrateurComponent } from './feature/administrateur/administrateur/administrateur';
import { Rapport } from './feature/rapport/rapport/rapport';
import { RhComponent } from './feature/rh/rh/rh';

import {
  authGuard,
  adminGuard,
  rhGuard,
  employeGuard,
  rhOrAdminGuard,
} from './services/authGuard/auth.guard';

export const routes: Routes = [
  { path: 'login', component: Login },
  {
    path: '',
    component: MainLayouts,
    canActivate: [authGuard],
    children: [
      { path: 'admin/dashboard-admin', component: DashboardAdmin, canActivate: [adminGuard] },
      { path: 'rh/dashboard-rh', component: DashboardRh, canActivate: [rhGuard] },
      {
        path: 'employe/dashboard-employe',
        component: DashboardEmploye,
        canActivate: [employeGuard],
      },

      { path: 'employees', component: Employee, canActivate: [rhOrAdminGuard] },
      { path: 'employees/create', component: Employee, canActivate: [rhOrAdminGuard] },
      { path: 'employees/edit/:id', component: Employee, canActivate: [rhOrAdminGuard] },
      { path: 'employees/view/:id', component: Employee, canActivate: [rhOrAdminGuard] },
      { path: 'employees/profil', component: Employee, canActivate: [employeGuard] },

      { path: 'rh', component: RhComponent, canActivate: [rhOrAdminGuard] },
      { path: 'rh/create', component: RhComponent, canActivate: [rhOrAdminGuard] },
      { path: 'rh/edit/:id', component: RhComponent, canActivate: [rhOrAdminGuard] },
      { path: 'rh/view/:id', component: RhComponent, canActivate: [rhOrAdminGuard] },
      { path: 'rh/profil', component: RhComponent, canActivate: [rhGuard] },

      { path: 'administrateurs', component: AdministrateurComponent, canActivate: [adminGuard] },
      {
        path: 'administrateurs/create',
        component: AdministrateurComponent,
        canActivate: [adminGuard],
      },
      {
        path: 'administrateurs/edit/:id',
        component: AdministrateurComponent,
        canActivate: [adminGuard],
      },
      {
        path: 'administrateurs/view/:id',
        component: AdministrateurComponent,
        canActivate: [adminGuard],
      },
      {
        path: 'administrateurs/profil',
        component: AdministrateurComponent,
        canActivate: [adminGuard],
      },

      { path: 'presences', component: PresenceListComponent, canActivate: [authGuard] },
      { path: 'conges', component: CongeComponent, canActivate: [authGuard] },
      { path: 'contrats', component: ContratsComponent, canActivate: [authGuard] },

      { path: 'postes', component: PostesComponent, canActivate: [rhOrAdminGuard] },
      { path: 'postes/create', component: PostesComponent, canActivate: [rhOrAdminGuard] },
      { path: 'postes/edit/:id', component: PostesComponent, canActivate: [rhOrAdminGuard] },

      { path: 'justifications', component: JustificationComponent, canActivate: [authGuard] },

      { path: 'rapport', component: Rapport, canActivate: [rhOrAdminGuard] },

      { path: 'notifications', component: NotificationsComponent, canActivate: [authGuard] },
    ],
  },

  { path: '', redirectTo: 'login', pathMatch: 'full' },
  { path: '**', component: PageNotFound },
];
