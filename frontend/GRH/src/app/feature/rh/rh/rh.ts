import {
  Component,
  OnInit,
  OnDestroy,
  inject,
  ChangeDetectorRef,
  ChangeDetectionStrategy,
} from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { RouterModule, ActivatedRoute, Router, NavigationEnd } from '@angular/router';
import { filter } from 'rxjs/operators';

import { RhService } from '../../../services/rh/rh';
import { RHModel } from '../../../models/rh';
import { AuthService, UtilisateurCourant } from '../../../services/auth/auth.service';
import { ThemeService } from '../../../services/Theme/theme-service';

@Component({
  selector: 'app-rh',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterModule],
  templateUrl: './rh.html',
  styleUrl: './rh.css',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class RhComponent implements OnInit, OnDestroy {
  // ── Injections ────────────────────────────────────────────
  private readonly rhService = inject(RhService);
  private readonly authService = inject(AuthService);
  private readonly cdr = inject(ChangeDetectorRef);
  private readonly route = inject(ActivatedRoute);
  private readonly router = inject(Router);
  readonly themeService = inject(ThemeService);

  // ── État principal ────────────────────────────────────────
  user: UtilisateurCourant = this.authService.getCurrentUser();
  rhs: RHModel[] = [];
  rhSelectionne: RHModel | null = null;
  monProfil: RHModel | null = null;

  modeAffichage: 'liste' | 'creation' | 'modification' | 'details' | 'profil' = 'liste';
  chargement = false;
  messageNotification = '';
  messageErreur = '';
  private _timer?: ReturnType<typeof setTimeout>;

  recherche = '';
  filtreStatut: boolean | null = null;
  nouveauRh: Partial<RHModel> = this.viderFormulaire();
  motDePasseActuel = '';
  nouveauMotDePasse = '';
  confirmMotDePasse = '';
  voirMdpActuel = false;
  voirNouveauMdp = false;
  voirConfirmMdp = false;
  erreurMdp = '';

  // ════════════════════════════════════════════════════════════
  //  CYCLE DE VIE
  // ════════════════════════════════════════════════════════════
  ngOnInit(): void {
    
    this.user = this.authService.getCurrentUser();
    this.detecterModeAffichage();

    // Écouter les changements d'URL
    this.router.events
      .pipe(filter((event) => event instanceof NavigationEnd))
      .subscribe(() => {
        this.detecterModeAffichage();
      });
  }

  ngOnDestroy(): void {
    this.nettoyerTimer();
  }

  // ════════════════════════════════════════════════════════════
  //  DÉTECTION DU MODE D'AFFICHAGE
  // ════════════════════════════════════════════════════════════
  private detecterModeAffichage(): void {
    const url = this.router.url;

    if (url.endsWith('/rh/profil') || url.includes('/rh/profil')) {
      this.modeAffichage = 'profil';
      this.chargerMonProfil();
    } else if (url.includes('/rh/create')) {
      if (this.peutCreerModifier) {
        this.modeAffichage = 'creation';
        this.nouveauRh = this.viderFormulaire();
      } else {
        this.router.navigate(['/rh']);
      }
    } else if (url.includes('/rh/edit/')) {
      if (this.peutCreerModifier) {
        const id = Number(this.route.snapshot.paramMap.get('id'));
        if (id) this.chargerRhPourModification(id);
      } else {
        this.router.navigate(['/rh']);
      }
    } else if (url.includes('/rh/view/')) {
      const id = Number(this.route.snapshot.paramMap.get('id'));
      if (id) this.chargerRhPourDetails(id);
    } else {
      this.modeAffichage = 'liste';
      this.chargerRhs();
    }

    this.cdr.markForCheck();
  }

  get userRole(): string {
    return (this.user?.role ?? '').toUpperCase();
  }

  get isRH(): boolean {
    return this.userRole === 'RH';
  }

  get isAdmin(): boolean {
    return this.userRole === 'ADMIN';
  }

  /** Seul l'ADMIN peut activer/désactiver */
  get peutGererComptes(): boolean {
    return this.isAdmin;
  }

  /** Admin et RH peuvent créer/modifier */
  get peutCreerModifier(): boolean {
    return this.isAdmin || this.isRH;
  }

  get isDarkMode(): boolean {
    return this.themeService.isDarkMode();
  }

  get rhsFiltres(): RHModel[] {
    const terme = this.recherche.toLowerCase().trim();
    return this.rhs.filter((r) => {
      const matchTexte =
        !terme ||
        (r.nom || '').toLowerCase().includes(terme) ||
        (r.prenom || '').toLowerCase().includes(terme) ||
        (r.email || '').toLowerCase().includes(terme);
      const matchStatut = this.filtreStatut === null || r.is_active === this.filtreStatut;
      return matchTexte && matchStatut;
    });
  }

  get nbActifs(): number {
    return this.rhs.filter((r) => r.is_active).length;
  }

  get nbInactifs(): number {
    return this.rhs.filter((r) => !r.is_active).length;
  }

  get forceMdp(): number {
    if (!this.nouveauMotDePasse) return 0;
    let force = 0;
    if (this.nouveauMotDePasse.length >= 8) force++;
    if (/[A-Z]/.test(this.nouveauMotDePasse)) force++;
    if (/[0-9]/.test(this.nouveauMotDePasse)) force++;
    if (/[^A-Za-z0-9]/.test(this.nouveauMotDePasse)) force++;
    return force;
  }

  chargerRhs(): void {
    this.chargement = true;
    this.cdr.markForCheck();

    this.rhService.getRhs().subscribe({
      next: (data) => {
        this.rhs = data;
        this.chargement = false;
        this.cdr.markForCheck();
      },
      error: (err) => {
        this.chargement = false;
        this.afficherErreur(err?.error?.detail || 'Erreur de chargement.');
        this.cdr.markForCheck();
      },
    });
  }

  chargerMonProfil(): void {
    if (!this.user?.id) {
      return;
    }

    this.chargement = true;
    this.cdr.markForCheck();

    this.rhService.getRh(this.user.id).subscribe({
      next: (data) => {
        this.monProfil = data;
        this.chargement = false;
        this.cdr.markForCheck();
      },
      error: (err) => {
        this.chargement = false;
        this.afficherErreur(err?.error?.detail || 'Erreur de chargement du profil.');
        this.cdr.markForCheck();
      },
    });
  }

  private chargerRhPourModification(id: number): void {
    this.rhService.getRh(id).subscribe({
      next: (data) => {
        this.rhSelectionne = data;
        this.modeAffichage = 'modification';
        this.cdr.markForCheck();
      },
      error: () => {
        this.afficherErreur('RH introuvable.');
        this.router.navigate(['/rh']);
      },
    });
  }

  private chargerRhPourDetails(id: number): void {
    this.rhService.getRh(id).subscribe({
      next: (data) => {
        this.rhSelectionne = data;
        this.modeAffichage = 'details';
        this.cdr.markForCheck();
      },
      error: () => {
        this.afficherErreur('RH introuvable.');
        this.router.navigate(['/rh']);
      },
    });
  }

  retournerALaListe(): void {
    this.modeAffichage = 'liste';
    this.rhSelectionne = null;
    this.nouveauRh = this.viderFormulaire();
    this.cdr.markForCheck();
    this.router.navigate(['/rh']);
  }

  voirDetails(rh: RHModel): void {
    this.rhSelectionne = { ...rh };
    this.modeAffichage = 'details';
    this.cdr.markForCheck();
  }

  selectionnerPourModification(rh: RHModel): void {
    this.rhSelectionne = { ...rh };
    this.modeAffichage = 'modification';
    this.cdr.markForCheck();
  }

  ouvrirMonProfil(): void {
    this.router.navigate(['/rh/profil']);
  }

  creerCompte(): void {
    if (!this.nouveauRh.email || !this.nouveauRh.nom || !this.nouveauRh.prenom) {
      this.afficherErreur('Veuillez remplir tous les champs obligatoires.');
      return;
    }

    this.chargement = true;
    this.cdr.markForCheck();

    this.rhService.creerRh(this.nouveauRh).subscribe({
      next: (res) => {
        this.afficherSucces(res.notification || 'Compte créé.');
        this.chargerRhs();
        this.retournerALaListe();
      },
      error: (err) => {
        this.afficherErreur(this.extraireMessageErreur(err));
        this.chargement = false;
        this.cdr.markForCheck();
      },
    });
  }

  enregistrerModification(): void {
    if (!this.rhSelectionne?.id) return;

    this.chargement = true;
    this.cdr.markForCheck();

    this.rhService.modifierRh(this.rhSelectionne.id, this.rhSelectionne).subscribe({
      next: () => {
        this.afficherSucces('Modifications enregistrées.');
        this.chargerRhs();
        this.retournerALaListe();
      },
      error: (err) => {
        this.afficherErreur(this.extraireMessageErreur(err));
        this.chargement = false;
        this.cdr.markForCheck();
      },
    });
  }

  activeCompte(id: number): void {
    if (!this.peutGererComptes) {
      this.afficherErreur('Seul un administrateur peut activer un compte.');
      return;
    }

    if (!confirm('Réactiver ce compte RH ?')) return;

    this.chargement = true;
    this.cdr.markForCheck();

    this.rhService.activerRh(id).subscribe({
      next: (res) => {
        this.afficherSucces(res.detail || 'Compte réactivé.');
        this.chargerRhs();
        if (this.rhSelectionne?.id === id) this.rhSelectionne.is_active = true;
        this.chargement = false;
        this.cdr.markForCheck();
      },
      error: (err) => {
        this.afficherErreur(err?.error?.detail || 'Erreur de réactivation.');
        this.chargement = false;
        this.cdr.markForCheck();
      },
    });
  }

  desactiverCompte(id: number): void {
    if (!this.peutGererComptes) {
      this.afficherErreur('Seul un administrateur peut désactiver un compte.');
      return;
    }

    if (!confirm('Désactiver ce compte RH ?')) return;

    this.chargement = true;
    this.cdr.markForCheck();

    this.rhService.desactiverRh(id).subscribe({
      next: (res) => {
        this.afficherSucces(res.detail || 'Compte désactivé.');
        this.chargerRhs();
        if (this.rhSelectionne?.id === id) this.rhSelectionne.is_active = false;
        this.chargement = false;
        this.cdr.markForCheck();
      },
      error: (err) => {
        this.afficherErreur(err?.error?.detail || 'Erreur de désactivation.');
        this.chargement = false;
        this.cdr.markForCheck();
      },
    });
  }


  sauvegarderProfil(): void {
    if (!this.monProfil?.id) return;

    this.chargement = true;
    this.cdr.markForCheck();

    this.rhService.modifierProfil(this.monProfil.id, this.monProfil).subscribe({
      next: () => {
        this.afficherSucces('Profil mis à jour.');
        this.chargement = false;
        this.cdr.markForCheck();
      },
      error: (err) => {
        this.afficherErreur(this.extraireMessageErreur(err));
        this.chargement = false;
        this.cdr.markForCheck();
      },
    });
  }

  annulerModifProfil(): void {
    this.chargerMonProfil();
    this.afficherSucces('Modifications annulées.');
  }

  changerMotDePasse(): void {
    this.erreurMdp = '';

    if (!this.motDePasseActuel || !this.nouveauMotDePasse || !this.confirmMotDePasse) {
      this.erreurMdp = 'Remplissez tous les champs.';
      this.cdr.markForCheck();
      return;
    }

    if (this.nouveauMotDePasse !== this.confirmMotDePasse) {
      this.erreurMdp = 'Les mots de passe ne correspondent pas.';
      this.cdr.markForCheck();
      return;
    }

    if (this.forceMdp < 2) {
      this.erreurMdp = 'Mot de passe trop faible.';
      this.cdr.markForCheck();
      return;
    }

    if (!this.monProfil?.id) return;

    this.chargement = true;
    this.cdr.markForCheck();

    //  Utiliser modifierProfil avec le mot de passe
    this.rhService
      .modifierProfil(this.monProfil.id, { password: this.nouveauMotDePasse })
      .subscribe({
        next: () => {
          this.afficherSucces('Mot de passe modifié.');
          this.motDePasseActuel = '';
          this.nouveauMotDePasse = '';
          this.confirmMotDePasse = '';
          this.chargement = false;
          this.cdr.markForCheck();
        },
        error: (err) => {
          this.erreurMdp = err?.error?.detail || 'Erreur.';
          this.chargement = false;
          this.cdr.markForCheck();
        },
      });
  }

  viderFormulaire(): Partial<RHModel> {
    return { email: '', nom: '', prenom: '', date_naissance: '', telephone: '' };
  }

  extraireMessageErreur(err: any): string {
    if (err?.error?.detail) return err.error.detail;
    if (err?.error && typeof err.error === 'object') {
      return Object.values(err.error).flat().join(' ') || 'Erreur.';
    }
    return 'Erreur serveur.';
  }

  afficherSucces(msg: string): void {
    this.nettoyerTimer();
    this.messageNotification = msg;
    this.messageErreur = '';
    this.cdr.markForCheck();
    this._timer = setTimeout(() => {
      this.messageNotification = '';
      this.cdr.markForCheck();
    }, 4000);
  }

  afficherErreur(msg: string): void {
    this.nettoyerTimer();
    this.messageErreur = msg;
    this.messageNotification = '';
    this.cdr.markForCheck();
    this._timer = setTimeout(() => {
      this.messageErreur = '';
      this.cdr.markForCheck();
    }, 5000);
  }

  nettoyerTimer(): void {
    if (this._timer) {
      clearTimeout(this._timer);
      this._timer = undefined;
    }
  }
}