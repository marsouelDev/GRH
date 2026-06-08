import { Component, OnInit, OnDestroy, ChangeDetectorRef, inject } from '@angular/core';
import { EmployeeService } from '../../../services/employee/employee-service';
import { EmployeModels } from '../../../models/employe';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ActivatedRoute, Router, RouterModule, NavigationEnd } from '@angular/router';
import { Subscription } from 'rxjs';
import { filter } from 'rxjs/operators';
import { ThemeService } from '../../../services/Theme/theme-service';
import { AuthService } from '../../../services/auth/auth.service';

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

  recherche = '';
  filtreStatut: boolean | null = null;

  messageNotification: string | null = null;
  messageErreur: string | null = null;

  modeAffichage: 'liste' | 'creation' | 'modification' | 'details' | 'profil' = 'liste';


  monProfil: EmployeModels | null = null;
  prefNotifEmail = false;

  // Changement de mot de passe
  motDePasseActuel = '';
  nouveauMotDePasse = '';
  confirmMotDePasse = '';
  voirMdpActuel = false;
  voirNouveauMdp = false;
  voirConfirmMdp = false;
  erreurMdp = false;


  themeService = inject(ThemeService);
  private authService = inject(AuthService);
  private routerSub!: Subscription;

  constructor(
    private employeService: EmployeeService,
    private router: Router,
    private route: ActivatedRoute,
    private cdr: ChangeDetectorRef,
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
    const url = this.router.url;

    if (url.includes('/create')) {
      this.modeAffichage = 'creation';
      this.nouveauEmploye = this.initialiserFormulaire();
      this.cdr.detectChanges();
    } else if (url.includes('/edit/')) {
      this.modeAffichage = 'modification';
      const id = this.route.snapshot.params['id'] || this.route.snapshot.paramMap.get('id');
      if (id) this.chargerEmployePourAction(Number(id));
    } else if (url.includes('/view/')) {
      this.modeAffichage = 'details';
      const id = this.route.snapshot.params['id'] || this.route.snapshot.paramMap.get('id');
      if (id) this.chargerEmployePourAction(Number(id));
    } else if (url.includes('/profil')) {
      this.modeAffichage = 'profil';
      this.chargerMonProfil();
    } else {
      this.modeAffichage = 'liste';
      this.chargerEmployes();
    }
  }

  get isDarkMode(): boolean {
    return this.themeService.isDarkMode();
  }

  get nbActifs(): number {
    return this.employes.filter((e) => e.is_active === true).length;
  }
  get nbInactifs(): number {
    return this.employes.filter((e) => !e.is_active).length;
  }

  get employesFiltres(): EmployeModels[] {
    return this.employes.filter((emp) => {
      const t = this.recherche.toLowerCase().trim();
      const matchRecherche =
        !t ||
        emp.nom.toLowerCase().includes(t) ||
        emp.prenom.toLowerCase().includes(t) ||
        emp.email.toLowerCase().includes(t);
      const matchStatut = this.filtreStatut === null || emp.is_active === this.filtreStatut;
      return matchRecherche && matchStatut;
    });
  }

  /** Force du mot de passe : 0-4 */
  get forceMdp(): number {
    const p = this.nouveauMotDePasse;
    if (!p) return 0;
    let score = 0;
    if (p.length >= 8) score++;
    if (/[A-Z]/.test(p)) score++;
    if (/[0-9]/.test(p)) score++;
    if (/[^a-zA-Z0-9]/.test(p)) score++;
    return score;
  }


  chargerEmployes(): void {
    this.employeService.getEmployes().subscribe({
      next: (data) => {
        this.employes = data;
        this.cdr.detectChanges();
      },
      error: () => {
        this.afficherErreur('Erreur de connexion avec le serveur.');
      },
    });
  }

  chargerEmployePourAction(id: number): void {
    this.employeService.getEmploye(id).subscribe({
      next: (data) => {
        this.employeSelectionne = data;
        this.cdr.detectChanges();
      },
      error: () => {
        this.afficherErreur('Impossible de charger cet employé.');
        this.retournerALaListe();
      },
    });
  }

  chargerMonProfil(): void {
    const user = this.authService.getCurrentUser();
    // Récupère l'employé connecté via son email ou id stocké dans le token
    this.employeService.getEmployes().subscribe({
      next: (data) => {
        this.monProfil = data.find((e) => e.email === user.email) || null;
        if (!this.monProfil) this.afficherErreur('Profil introuvable.');
        this.cdr.detectChanges();
      },
      error: () => {
        this.afficherErreur('Impossible de charger votre profil.');
      },
    });
  }


  creerCompte(): void {
    this.employeService.createEmploye(this.nouveauEmploye).subscribe({
      next: (res: any) => {
        this.afficherSucces(res.notification || 'Employé créé avec succès.');
        this.nouveauEmploye = this.initialiserFormulaire();
        this.cdr.detectChanges();
        setTimeout(() => this.retournerALaListe(), 3000);
      },
      error: () => {
        this.afficherErreur("Échec de la création de l'employé.");
      },
    });
  }

  enregistrerModification(): void {
    if (!this.employeSelectionne?.id) return;
    this.employeService
      .updateEmploye(this.employeSelectionne.id, this.employeSelectionne)
      .subscribe({
        next: () => {
          this.afficherSucces('Modifications enregistrées avec succès.');
          this.employeSelectionne = null;
          this.cdr.detectChanges();
          setTimeout(() => this.retournerALaListe(), 2000);
        },
        error: () => {
          this.afficherErreur('Échec de la modification.');
        },
      });
  }

  activeCompte(id: number): void {
    this.employeService.activeEmploye(id).subscribe({
      next: (res: any) => {
        this.afficherSucces(res.detail || 'Employé activé avec succès.');
        const idx = this.employes.findIndex((e) => e.id === id);
        if (idx !== -1) this.employes[idx].is_active = true;
        this.cdr.detectChanges();
        this.chargerEmployes();
      },
      error: (err) => {
        this.afficherErreur(err.error?.detail || "Impossible d'activer ce compte.");
      },
    });
  }

  desactiverCompte(id: number): void {
    this.employeService.deleteEmploye(id).subscribe({
      next: (res: any) => {
        this.afficherSucces(res.detail || 'Employé désactivé avec succès.');
        const idx = this.employes.findIndex((e) => e.id === id);
        if (idx !== -1) this.employes[idx].is_active = false;
        this.cdr.detectChanges();
        this.chargerEmployes();
      },
      error: (err) => {
        this.afficherErreur(err.error?.detail || 'Impossible de désactiver ce compte.');
      },
    });
  }

  
  //  PROFIL — SAUVEGARDE & MOT DE PASSE

  sauvegarderProfil(): void {
    if (!this.monProfil?.id) return;

    this.employeService
      .updateProfil(this.monProfil.id, {
        nom: this.monProfil.nom,
        prenom: this.monProfil.prenom,
        email: this.monProfil.email,
        telephone: this.monProfil.telephone,
        date_naissance: this.monProfil.date_naissance,
      })
      .subscribe({
        next: () => {
          this.afficherSucces('Profil mis à jour avec succès.');
        },
        error: (err) => {
          this.afficherErreur(err?.error?.detail || 'Impossible de sauvegarder le profil.');
        },
      });
  }

  changerMotDePasse(): void {
    this.erreurMdp = false;

    if (!this.motDePasseActuel || !this.nouveauMotDePasse || !this.confirmMotDePasse) {
      this.afficherErreur('Remplissez tous les champs de mot de passe.');
      return;
    }

    if (this.nouveauMotDePasse !== this.confirmMotDePasse) {
      this.erreurMdp = true;
      this.afficherErreur('Les mots de passe ne correspondent pas.');
      return;
    }

    if (this.forceMdp < 2) {
      this.afficherErreur('Mot de passe trop faible. Ajoutez des chiffres et des majuscules.');
      return;
    }

    if (!this.monProfil?.id) return;

    this.employeService
      .updateProfil(this.monProfil.id, {
        password: this.nouveauMotDePasse,
      })
      .subscribe({
        next: () => {
          this.afficherSucces('Mot de passe mis à jour avec succès.');
          this.motDePasseActuel = '';
          this.nouveauMotDePasse = '';
          this.confirmMotDePasse = '';
          this.erreurMdp = false;
        },
        error: (err) => {
          this.afficherErreur(err?.error?.detail || 'Impossible de changer le mot de passe.');
        },
      });
  }


  annulerModifProfil(): void {
    this.chargerMonProfil(); // recharge depuis le serveur
  }


  voirDetails(emp: EmployeModels): void {
    if (emp.id) this.router.navigate(['/employees/view', emp.id]);
  }

  selectionnerPourModification(emp: EmployeModels): void {
    if (emp.id) this.router.navigate(['/employees/edit', emp.id]);
  }

  retournerALaListe(): void {
    this.router.navigate(['/employees']);
  }

  ouvrirProfil(): void {
    this.router.navigate(['/employees/profil']);
  }

  private initialiserFormulaire(): EmployeModels {
    return { email: '', nom: '', prenom: '', date_naissance: '', telephone: '', salaire: 0 };
  }

  private afficherSucces(msg: string): void {
    this.messageNotification = msg;
    this.messageErreur = null;
    this.cdr.detectChanges();
    setTimeout(() => {
      this.messageNotification = null;
      this.cdr.detectChanges();
    }, 3000);
  }

  private afficherErreur(msg: string): void {
    this.messageErreur = msg;
    this.messageNotification = null;
    this.cdr.detectChanges();
    setTimeout(() => {
      this.messageErreur = null;
      this.cdr.detectChanges();
    }, 3000);
  }
  
  
}
