import { Component } from '@angular/core';
import { FormBuilder, FormGroup, Validators, ReactiveFormsModule } from '@angular/forms';
import { HttpClient } from '@angular/common/http';
import { Router } from '@angular/router';
import { NgIf } from '@angular/common';
import { email } from '@angular/forms/signals';
import { jwtDecode } from 'jwt-decode'; 

interface CustomJwtPayload {
  role?: string;      // Le champ rôle envoyé par votre backend
  user_id?: number;
  exp?: number;
}

@Component({
  selector: 'app-login',
  imports: [ ReactiveFormsModule,NgIf],
  templateUrl: './login.html',
  styleUrl: './login.css',
})
export class Login {
   loginForm: FormGroup;
  errorMessage: string = '';

  constructor(
    private fb: FormBuilder,
    private http: HttpClient,
    private router: Router
  ) {
    this.loginForm = this.fb.group({
      email: ['', [Validators.required, Validators.email]],
      password: ['', [Validators.required]]
    });
  }

  onSubmit(): void {
    if (this.loginForm.invalid) return;

    this.http.post<any>('http://localhost:8000/api/token/', this.loginForm.value).subscribe({
      next: (response) => {
        //  Sauvegarde du token d'accès pour l'intercepteur
        localStorage.setItem('access_token', response.access);
        
        try {
          //  Décodage du token pour récupérer le vrai rôle de l'utilisateur
          const decoded = jwtDecode<CustomJwtPayload>(response.access);
          
          //  Récupération du rôle (si absent du token, on applique 'EMPLOYE' par défaut)
          const userRole = decoded.role || 'EMPLOYE'; 
          
        
          localStorage.setItem('user_role', userRole);
          
        
          this.router.navigate(['/employes']);
          
        } catch (error) {
         
          localStorage.setItem('user_role', 'EMPLOYE');
          this.router.navigate(['/employes']);
        }
      },
      error: (err) => {
        this.errorMessage = "Email ou mot de passe incorrect.";
      }
    });
  }
}