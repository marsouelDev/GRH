import { Routes } from '@angular/router';
import { Login } from './components/login/login';
import { PageNotFound } from './components/page-not-found/page-not-found';

export const routes: Routes = [
    {path : 'login' , component : Login},
    {path : 'page-not-found' , component : PageNotFound },
    
];
