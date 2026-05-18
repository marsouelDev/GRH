import { Routes } from '@angular/router';
import { Login } from './components/login/login';

export const routes: Routes = [
    {path : 'accuiel' , component : Login},
    { path: '**', redirectTo: 'login' }
];
