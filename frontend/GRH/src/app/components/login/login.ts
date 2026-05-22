import { Component, inject } from '@angular/core';
import { FormBuilder, FormGroup, Validators, ReactiveFormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { NgIf } from '@angular/common';
import { AuthService } from '../../services/auth/auth.service';

@Component({
  selector: 'app-login',
  imports: [ReactiveFormsModule, NgIf],
  templateUrl: './login.html',
  styleUrl: './login.css',
})
export class Login {
  loginForm: FormGroup;
  errorMessage: string | null = null;
  isLoading: boolean = false;
  showPassword: boolean = false;

  private fb = inject(FormBuilder);
  private router = inject(Router);
  private authService = inject(AuthService);

  constructor() {
    this.loginForm = this.fb.group({
      email: ['', [Validators.required, Validators.email]],
      password: ['', [Validators.required]],
    });
  }

  togglePasswordVisibility(): void {
    this.showPassword = !this.showPassword;
  }

  onSubmit(): void {
    if (this.loginForm.invalid || this.isLoading) return;

    this.isLoading = true;
    this.errorMessage = null;

    // Utilisation de la méthode centralisée du service
    this.authService.login(this.loginForm.value).subscribe({
      next: () => {
        
        this.isLoading = false;

        if (this.authService.isAdmin()) {
          this.router.navigate(['/page']);
        } else if (this.authService.isRH()) {
          // Correction ici : auth -> authService
          this.router.navigate(['/dashboard-rh']);
        } else {
          this.router.navigate(['/page']);
        }
      },
      error: (err) => {
        this.isLoading = false;
        this.errorMessage = 'Email ou mot de passe incorrect.';
        console.error(err);
      },
    });
  }
}
