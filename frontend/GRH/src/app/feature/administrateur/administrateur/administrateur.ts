import { Component, OnInit, OnDestroy, ChangeDetectorRef, inject } from '@angular/core';
import { AdministrateurService } from '../../../services/administrateur/administrateur';
import { AdministrateursModels } from '../../../models/administrateur';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ActivatedRoute, Router, RouterModule, NavigationEnd } from '@angular/router';
import { Subscription } from 'rxjs';
import { filter } from 'rxjs/operators';
import { ThemeService } from '../../../services/Theme/theme-service';

@Component({
  selector: 'app-administrateur',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterModule],
  templateUrl: './administrateur.html',
  styleUrl: './administrateur.css',
})
export class AdministrateurComponent implements OnInit, OnDestroy {
  employes: AdministrateursModels[] = [];
  nouveauEmploye: AdministrateursModels = this.initialiserFormulaire();
  employeSelectionne: AdministrateursModels | null = null;

  recherche: string = '';
  filtreStatut: boolean | null = null;

  messageNotification: string | null = null;
  messageErreur: string | null = null;
  chargement: boolean = false;

  modeAffichage: 'liste' | 'creation' | 'modification' | 'details' | 'profil' = 'liste';

  monProfil: AdministrateursModels | null = null;
  motDePasseActuel: string = '';
  nouveauMotDePasse: string = '';
  confirmMotDePasse: string = '';
  voirMdpActuel: boolean = false;
  voirNouveauMdp: boolean = false;
  voirConfirmMdp: boolean = false;
  prefNotifEmail: boolean = true;
  erreurMdp: boolean = false;

  private routerSub!: Subscription;
  private _timer?: ReturnType<typeof setTimeout>;

  themeService = inject(ThemeService);

  constructor(
    private administrateurService: AdministrateurService,
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
    if (this.routerSub) this.routerSub.unsubscribe();
    if (this._timer) clearTimeout(this._timer);
  }

  // ── Getters ─────────────────────────────────────────────
  get isDarkMode(): boolean {
    return this.themeService.isDarkMode();
  }

  get forceMdp(): number {
    const mdp = this.nouveauMotDePasse;
    if (!mdp) return 0;
    let force = 0;
    if (mdp.length >= 8) force++;
    if (/[A-Z]/.test(mdp)) force++;
    if (/[0-9]/.test(mdp)) force++;
    if (/[^A-Za-z0-9]/.test(mdp)) force++;
    return force;
  }

  get nbTotal(): number {
    return this.employes.length;
  }

  get employesFiltres(): AdministrateursModels[] {
    return this.employes.filter((emp) => {
      const terme = this.recherche.toLowerCase().trim();
      return (
        !terme ||
        emp.nom?.toLowerCase().includes(terme) ||
        emp.prenom?.toLowerCase().includes(terme) ||
        emp.email?.toLowerCase().includes(terme)
      );
    });
  }

  // ── Navigation ──────────────────────────────────────────
  analyserUrl(): void {
    const url = this.router.url;

    if (url.includes('/create')) {
      this.modeAffichage = 'creation';
      this.nouveauEmploye = this.initialiserFormulaire();
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
    this.cdr.detectChanges();
  }

  retournerALaListe(): void {
    this.router.navigate(['/administrateurs']);
  }

  // ── Chargement ──────────────────────────────────────────
  chargerEmployes(): void {
    this.chargement = true;
    this.administrateurService.getAdministrateurs().subscribe({
      next: (data) => {
        this.employes = data;
        this.chargement = false;
        this.cdr.detectChanges();
      },
      error: () => {
        this.afficherErreur('Erreur de connexion avec le serveur.');
        this.chargement = false;
      },
    });
  }

  chargerEmployePourAction(id: number): void {
    this.chargement = true;
    this.administrateurService.getAdministrateur(id).subscribe({
      next: (data) => {
        this.employeSelectionne = data;
        this.chargement = false;
        this.cdr.detectChanges();
      },
      error: () => {
        this.afficherErreur('Impossible de charger cet administrateur.');
        this.chargement = false;
        setTimeout(() => this.retournerALaListe(), 2000);
      },
    });
  }

  chargerMonProfil(): void {
    const userId = localStorage.getItem('user_id');
    if (!userId) {
      this.afficherErreur('Utilisateur non connecté.');
      return;
    }
    this.chargement = true;
    this.administrateurService.getAdministrateur(Number(userId)).subscribe({
      next: (data) => {
        this.monProfil = data;
        this.chargement = false;
        this.cdr.detectChanges();
      },
      error: () => {
        this.afficherErreur('Impossible de charger votre profil.');
        this.chargement = false;
      },
    });
  }

  // ── Formulaire ──────────────────────────────────────────
  initialiserFormulaire(): AdministrateursModels {
    return {
      id: undefined,
      email: '',
      nom: '',
      prenom: '',
      date_naissance: '',
      telephone: '',
      is_active: true,
    };
  }

  creerCompte(): void {
    if (this.chargement) return;
    if (!this.nouveauEmploye.email || !this.nouveauEmploye.nom || !this.nouveauEmploye.prenom) {
      this.afficherErreur('Veuillez remplir tous les champs obligatoires.');
      return;
    }

    this.chargement = true;
    this.administrateurService.createAdministrateur(this.nouveauEmploye).subscribe({
      next: (reponse: any) => {
        this.afficherSucces(reponse.notification || 'Administrateur créé avec succès.');
        this.nouveauEmploye = this.initialiserFormulaire();
        setTimeout(() => this.retournerALaListe(), 1500);
      },
      error: (err) => {
        this.afficherErreur(err?.error?.detail || 'Échec de la création.');
        this.chargement = false;
      },
    });
  }

  enregistrerModification(): void {
    if (!this.employeSelectionne?.id || this.chargement) return;

    this.chargement = true;
    this.administrateurService
      .updateAdministrateur(this.employeSelectionne.id, this.employeSelectionne)
      .subscribe({
        next: () => {
          this.afficherSucces('Modifications enregistrées avec succès.');
          setTimeout(() => this.retournerALaListe(), 1500);
        },
        error: (err) => {
          this.afficherErreur(err?.error?.detail || 'Échec de la modification.');
          this.chargement = false;
        },
      });
  }

  // ── Navigation ──────────────────────────────────────────
  voirDetails(employe: AdministrateursModels): void {
    if (employe.id) this.router.navigate(['/administrateurs/view', employe.id]);
  }

  selectionnerPourModification(employe: AdministrateursModels): void {
    if (employe.id) this.router.navigate(['/administrateurs/edit', employe.id]);
  }

  // ── Profil ──────────────────────────────────────────────
  sauvegarderProfil(): void {
    if (!this.monProfil?.id || this.chargement) return;

    this.chargement = true;
    this.administrateurService.updateProfil(this.monProfil.id, this.monProfil).subscribe({
      next: () => {
        this.afficherSucces('Profil mis à jour avec succès.');
        this.chargement = false;
      },
      error: (err) => {
        this.afficherErreur(err?.error?.detail || 'Échec de la mise à jour.');
        this.chargement = false;
      },
    });
  }

  annulerModifProfil(): void {
    this.chargerMonProfil();
  }

  changerMotDePasse(): void {
    if (!this.nouveauMotDePasse || !this.confirmMotDePasse) {
      this.afficherErreur('Veuillez remplir tous les champs.');
      return;
    }
    if (this.nouveauMotDePasse !== this.confirmMotDePasse) {
      this.afficherErreur('Les mots de passe ne correspondent pas.');
      return;
    }
    if (this.forceMdp < 2) {
      this.afficherErreur('Le mot de passe est trop faible.');
      return;
    }
    if (!this.monProfil?.id) return;

    this.chargement = true;
    this.administrateurService
      .updateProfil(this.monProfil.id, { password: this.nouveauMotDePasse })
      .subscribe({
        next: () => {
          this.afficherSucces('Mot de passe modifié avec succès.');
          this.motDePasseActuel = '';
          this.nouveauMotDePasse = '';
          this.confirmMotDePasse = '';
          this.chargement = false;
        },
        error: (err) => {
          this.afficherErreur(err?.error?.detail || 'Échec du changement.');
          this.chargement = false;
        },
      });
  }

  // ── Notifications ───────────────────────────────────────
  private afficherSucces(msg: string): void {
    clearTimeout(this._timer);
    this.messageNotification = msg;
    this.messageErreur = null;
    this._timer = setTimeout(() => {
      this.messageNotification = null;
      this.cdr.detectChanges();
    }, 3000);
  }

  private afficherErreur(msg: string): void {
    clearTimeout(this._timer);
    this.messageErreur = msg;
    this.messageNotification = null;
    this._timer = setTimeout(() => {
      this.messageErreur = null;
      this.cdr.detectChanges();
    }, 4000);
  }
}
