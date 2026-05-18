import { Component, inject } from '@angular/core'; 
import { FormBuilder, FormGroup, Validators, ReactiveFormsModule } from '@angular/forms';
import { HttpClient } from '@angular/common/http';
import { Router } from '@angular/router';
import { NgIf } from '@angular/common';
import { jwtDecode } from 'jwt-decode'; 

interface CustomJwtPayload {
  role?: string;      
  user_id?: number;
  exp?: number;
}

@Component({
  selector: 'app-login',
  imports: [ReactiveFormsModule, NgIf],
  templateUrl: './login.html',
  styleUrl: './login.css',
})
export class Login {
  loginForm: FormGroup;
  errorMessage: string = '';

  private fb = inject(FormBuilder);
  private http = inject(HttpClient);
  private router = inject(Router);

  constructor() {
    // Initialisation propre du formulaire
    this.loginForm = this.fb.group({
      email: ['', [Validators.required, Validators.email]],
      password: ['', [Validators.required]]
    });
  }

  onSubmit(): void {
    if (this.loginForm.invalid) return;

    this.http.post<any>('http://localhost:8000/api/token/', this.loginForm.value).subscribe({
      next: (response: any) => { 
        // Sauvegarde du token d'accès pour l'intercepteur
        localStorage.setItem('access_token', response.access);
        
        try {
          // Décodage du token pour récupérer le vrai rôle de l'utilisateur
          const decoded = jwtDecode<CustomJwtPayload>(response.access);
          
          const userRole = decoded.role || 'EMPLOYE'; 
          
          localStorage.setItem('user_role', userRole);
          
          // Redirection
          this.router.navigate(['/']);
          
        } catch (error) {
          localStorage.setItem('user_role', 'EMPLOYE');
          this.router.navigate(['/employes']);
        }
      },
      error: (err: any) => {
        this.errorMessage = "Email ou mot de passe incorrect.";
      }
    });
  }
}
