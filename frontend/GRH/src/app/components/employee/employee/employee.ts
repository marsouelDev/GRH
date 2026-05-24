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
  
  // Variables pour l'affichage des bannières HTML
  messageNotification: string | null = null;
  messageErreur: string | null = null;

  modeAffichage: 'liste' | 'creation' | 'modification' = 'liste';
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

    this.analyserUrl();
  }

  ngOnDestroy(): void {
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
        this.messageErreur = "Impossible de charger cet employé.";
        this.masquerNotifications();
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
      error: (err) => {
        console.error('Erreur de chargement', err);
        this.messageErreur = "Erreur de connexion avec le serveur.";
        this.masquerNotifications();
      },
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
      error: (err) => {
        console.error('Erreur de création', err);
        this.messageErreur = "Échec de la création de l'employé.";
        this.masquerNotifications();
      },
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
            this.messageNotification = "Modifications enregistrées avec succès.";
            this.employeSelectionne = null;
            setTimeout(() => {
              this.messageNotification = null;
              this.retournerALaListe();
            }, 2000);
          },
          error: (err) => {
            console.error('Erreur de modification', err);
            this.messageErreur = "Échec de la modification.";
            this.masquerNotifications();
          },
        });
    }
  }

  activeCompte(id: number): void {
    this.employeService.activeEmploye(id).subscribe({
      next: (reponse) => {
        this.messageNotification = reponse.detail || 'Employé activé avec succès.';
        
        // Synchronisation locale
        const index = this.employes.findIndex(e => e.id === id);
        if (index !== -1) this.employes[index].is_active = true;
        if (this.employeSelectionne && this.employeSelectionne.id === id) this.employeSelectionne.is_active = true;

        this.masquerNotifications();
        this.chargerEmployes();
      },
      error: (err) => {
        console.error("Erreur d'activation", err);
        this.messageErreur = "Impossible d'activer ce compte.";
        this.masquerNotifications();
      },
    });
  }

  desactiverCompte(id: number): void {
    this.employeService.deleteEmploye(id).subscribe({
      next: (reponse) => {
        this.messageNotification = reponse.detail || 'Employé désactivé avec succès.';
        
        // Synchronisation locale
        const index = this.employes.findIndex(e => e.id === id);
        if (index !== -1) this.employes[index].is_active = false;

        this.masquerNotifications();
        this.chargerEmployes();
      },
      error: (err) => {
        console.error('Erreur de désactivation', err);
        this.messageErreur = "Impossible de désactiver ce compte.";
        this.masquerNotifications();
      },
    });
  }

  private masquerNotifications(): void {
    setTimeout(() => {
      this.messageNotification = null;
      this.messageErreur = null;
    }, 3000);
  }

  retournerALaListe(): void {
    this.router.navigate(['/employees']);
  }
}
