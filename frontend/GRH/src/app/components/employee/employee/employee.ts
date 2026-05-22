import { Component, OnInit, OnDestroy } from '@angular/core';
import { EmployeeService } from '../../../services/employee/employee-service';
import { EmployeModels } from '../../../models/employe';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ActivatedRoute, Router, RouterModule, NavigationEnd } from '@angular/router';
import { Subscription } from 'rxjs';
import { filter } from 'rxjs/operators';

@Component({
  selector: 'app-employee',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterModule],
  templateUrl: './employee.html',
  styleUrl: './employee.css',
})
export class Employee implements OnInit, OnDestroy {
  employes: EmployeModels[] = [];
  nouveauEmploye: EmployeModels = this.initialiserFormulaire();
  employeSelectionne: EmployeModels | null = null;
  messageNotification: string | null = null;

  modeAffichage: 'liste' | 'creation' | 'modification' = 'liste';

  // CORRECTION : stocker l'abonnement pour le désinscrire à la destruction
  private routerSub!: Subscription;

  constructor(
    private employeService: EmployeeService,
    private router: Router,
    private route: ActivatedRoute,
  ) {}

  ngOnInit(): void {
    this.routerSub = this.router.events
      .pipe(filter((e) => e instanceof NavigationEnd))
      .subscribe(() => this.analyserUrl());

    // Appel initial au chargement
    this.analyserUrl();
  }

  ngOnDestroy(): void {
    // Nettoyage de l'abonnement pour éviter les fuites mémoire
    this.routerSub?.unsubscribe();
  }

  analyserUrl(): void {
    const urlCourante = this.router.url;

    if (urlCourante.includes('/create')) {
      this.modeAffichage = 'creation';
      this.nouveauEmploye = this.initialiserFormulaire();
    } else if (urlCourante.includes('/edit/')) {
      this.modeAffichage = 'modification';
      const idUrl = this.route.snapshot.params['id'];
      if (idUrl) {
        this.chargerEmployePourModification(Number(idUrl));
      }
    } else {
      this.modeAffichage = 'liste';
      this.chargerEmployes();
    }
  }

  chargerEmployePourModification(id: number): void {
    this.employeService.getEmploye(id).subscribe({
      next: (data) => (this.employeSelectionne = data),
      error: (err) => {
        console.error("Erreur lors du chargement de l'employé", err);
        this.retournerALaListe();
        
      },
    });
  }

  initialiserFormulaire(): EmployeModels {
    return { email: '', nom: '', prenom: '', date_naissance: '', telephone: '', salaire: 0 };
  }

  chargerEmployes(): void {
    this.employeService.getEmployes().subscribe({
      next: (data) => (this.employes = data),
      error: (err) => console.error('Erreur de chargement', err),
    });
  }

  creerCompte(): void {
    this.employeService.createEmploye(this.nouveauEmploye).subscribe({
      next: (reponse: any) => {
        this.messageNotification = reponse.notification || 'Employé créé avec succès.';
        this.nouveauEmploye = this.initialiserFormulaire();
        setTimeout(() => {
          this.messageNotification = null;
          this.retournerALaListe();
        }, 3000);
      },
      error: (err) => console.error('Erreur de création', err),
    });
  }

  selectionnerPourModification(employe: EmployeModels): void {
    this.router.navigate(['/employees/edit', employe.id]);
  }

  enregistrerModification(): void {
    if (this.employeSelectionne && this.employeSelectionne.id) {
      this.employeService
        .updateEmploye(this.employeSelectionne.id, this.employeSelectionne)
        .subscribe({
          next: () => {
            this.employeSelectionne = null;
            this.retournerALaListe();
          },
          error: (err) => console.error('Erreur de modification', err),
        });
    }
  }

  desactiverCompte(id: number): void {
    if (confirm('Voulez-vous vraiment désactiver cet employé ?')) {
      this.employeService.deleteEmploye(id).subscribe({
        next: (reponse) => {
          alert(reponse.detail);
          this.chargerEmployes();
        },
        error: (err) => console.error('Erreur de désactivation', err),
      });
    }
  }

  retournerALaListe(): void {
    this.router.navigate(['/employees']);
  }
}
