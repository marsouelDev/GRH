import {
  Component,
  OnInit,
  OnDestroy,
  inject,
  ChangeDetectionStrategy,
  ChangeDetectorRef,
} from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule, NgForm } from '@angular/forms';
import { ActivatedRoute, Router, RouterModule } from '@angular/router';
import { PosteService } from '../../../services/poste/poste-services';
import { PosteModel, NiveauHierarchie } from '../../../models/poste';
import { AuthService } from '../../../services/auth/auth.service';

@Component({
  selector: 'app-postes',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterModule],
  templateUrl: './poste.html',
  styleUrl: './poste.css',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class PostesComponent implements OnInit, OnDestroy {
  private posteService = inject(PosteService);
  private route = inject(ActivatedRoute);
  private router = inject(Router);
  private cdr = inject(ChangeDetectorRef);
  private authService = inject(AuthService);

  // ── Configuration des niveaux ─────────────────────────────
  readonly niveaux: {
    value: NiveauHierarchie;
    label: string;
    icon: string;
    badgeClass: string;
  }[] = [
    {
      value: 'JUNIOR',
      label: 'Junior',
      icon: 'bi-person-fill',
      badgeClass: 'niveau-badge--junior',
    },
    {
      value: 'INTERMEDIAIRE',
      label: 'Intermédiaire',
      icon: 'bi-person-check-fill',
      badgeClass: 'niveau-badge--intermediaire',
    },
    { value: 'SENIOR', label: 'Senior', icon: 'bi-award-fill', badgeClass: 'niveau-badge--senior' },
    {
      value: 'MANAGER',
      label: 'Manager',
      icon: 'bi-people-fill',
      badgeClass: 'niveau-badge--manager',
    },
    {
      value: 'DIRECTEUR',
      label: 'Directeur',
      icon: 'bi-star-fill',
      badgeClass: 'niveau-badge--directeur',
    },
  ];

  // ── État ──────────────────────────────────────────────────
  tousLesPostes: PosteModel[] = [];
  postes: PosteModel[] = [];
  modeAffichage: 'liste' | 'creation' | 'edition' = 'liste';
  voirArchives = false;
  recherche = '';
  filtreNiveau: NiveauHierarchie | '' = '';
  filtreStatut: 'actif' | 'archive' | '' = '';
  errorMessage = '';
  successMessage = '';
  isRH = false;
  isAdmin = false;
  isManager = false;
  posteSelectionne: Partial<PosteModel> = this.initialiserFormulaire();
  afficherModalConfirmation = false;
  modalConfirmationConfig: {
    type: 'success' | 'warning' | 'danger';
    titre: string;
    message: string;
    action: 'archiver' | 'reactiver' | 'autre';
  } | null = null;
  posteAActionnerId?: number;

  private _msgTimer?: ReturnType<typeof setTimeout>;

  // ════════════════════════════════════════════════════════════
  //  CYCLE DE VIE
  // ════════════════════════════════════════════════════════════

  ngOnInit(): void {
    this.detecterRoleUtilisateur();
    this.route.url.subscribe(() => {
      this.analyserUrlEtContext();
    });
  }

  ngOnDestroy(): void {
    clearTimeout(this._msgTimer);
  }

  // ════════════════════════════════════════════════════════════
  //  RÔLES
  // ════════════════════════════════════════════════════════════

  private detecterRoleUtilisateur(): void {
    const user = this.authService.getCurrentUser();
    const role = (user?.role || '').toUpperCase();

    this.isRH = role === 'RH';
    this.isAdmin = role === 'ADMIN';
    this.isManager = this.isRH || this.isAdmin;

    console.log('👤 Rôles détectés:', {
      role,
      isRH: this.isRH,
      isAdmin: this.isAdmin,
      isManager: this.isManager,
    });
  }

  private analyserUrlEtContext(): void {
    const url = this.router.url;

    if (url.includes('/create')) {
      this.modeAffichage = 'creation';
      this.posteSelectionne = this.initialiserFormulaire();
    } else if (url.includes('/edit/')) {
      this.modeAffichage = 'edition';
      const id = Number(this.route.snapshot.paramMap.get('id'));
      if (id) this.chargerDetailPoste(id);
    } else {
      this.modeAffichage = 'liste';
      this.chargerPostes();
    }
  }


  get nbPostesActifs(): number {
    return this.tousLesPostes.filter((p) => p.est_actif).length;
  }

  get nbPostesArchives(): number {
    return this.tousLesPostes.filter((p) => !p.est_actif).length;
  }

  get nbDirecteurs(): number {
    return this.tousLesPostes.filter((p) => p.niveau_hierarchie === 'DIRECTEUR').length;
  }

  get nbParNiveau(): { [key: string]: number } {
    const result: { [key: string]: number } = {};
    this.niveaux.forEach((n) => {
      result[n.value] = this.tousLesPostes.filter((p) => p.niveau_hierarchie === n.value).length;
    });
    return result;
  }

  isDescriptionLongue(description: string | undefined | null): boolean {
    return (description?.length ?? 0) > 60;
  }

  // ════════════════════════════════════════════════════════════
  //  CHARGEMENT DES DONNÉES
  // ════════════════════════════════════════════════════════════

  chargerPostes(): void {
    this.errorMessage = '';

    this.posteService.getPostes(true).subscribe({
      next: (data) => {
        this.tousLesPostes = data;
        this.appliquerFiltres();
        this.cdr.markForCheck();
      },
      error: (err) => {
        this.afficherErreur('Erreur lors du chargement des postes.');
        this.cdr.markForCheck();
      },
    });
  }

  chargerDetailPoste(id: number): void {
    this.posteService.getPoste(id).subscribe({
      next: (data) => {
        this.posteSelectionne = { ...data };
        this.cdr.markForCheck();
      },
      error: (err) => {
        this.afficherErreur('Impossible de charger les détails du poste.');
        this.cdr.markForCheck();
        this.router.navigate(['/postes']);
      },
    });
  }

  // ════════════════════════════════════════════════════════════
  //  FILTRES
  // ════════════════════════════════════════════════════════════

  toggleArchives(): void {
    this.voirArchives = !this.voirArchives;
    this.appliquerFiltres();
  }

  appliquerFiltres(): void {
    let result = [...this.tousLesPostes];

    // 1. Filtre archives (bouton principal)
    if (this.voirArchives) {
      result = result.filter((p) => !p.est_actif);
    } else {
      result = result.filter((p) => p.est_actif);
    }

    // 2. Filtre par niveau hiérarchique
    if (this.filtreNiveau) {
      result = result.filter((p) => p.niveau_hierarchie === this.filtreNiveau);
    }

    // 3. Filtre par statut (actif/archivé) - indépendant du toggle principal
    if (this.filtreStatut === 'actif') {
      result = result.filter((p) => p.est_actif);
    } else if (this.filtreStatut === 'archive') {
      result = result.filter((p) => !p.est_actif);
    }

    // 4. Recherche textuelle
    if (this.recherche.trim()) {
      const terme = this.recherche.toLowerCase().trim();
      result = result.filter((p) => {
        const intitule = (p.intitule || '').toLowerCase();
        const description = (p.description || '').toLowerCase();
        const niveau = this.getLabelForNiveau(p.niveau_hierarchie).toLowerCase();
        return intitule.includes(terme) || description.includes(terme) || niveau.includes(terme);
      });
    }

    this.postes = result;
    this.cdr.markForCheck();
  }

  reinitialiserFiltres(): void {
    this.recherche = '';
    this.filtreNiveau = '';
    this.filtreStatut = '';
    this.voirArchives = false;
    this.appliquerFiltres();
  }

  setFiltreNiveau(niveau: NiveauHierarchie | ''): void {
    this.filtreNiveau = niveau;
    this.appliquerFiltres();
  }

  setFiltreStatut(statut: 'actif' | 'archive' | ''): void {
    this.filtreStatut = statut;
    this.appliquerFiltres();
  }


  soumettrePoste(form: NgForm): void {
    if (form.invalid) {
      Object.keys(form.controls).forEach((key) => {
        form.controls[key].markAsTouched();
      });
      return;
    }

    const payload = { ...this.posteSelectionne } as PosteModel;

    if (this.modeAffichage === 'edition' && this.posteSelectionne.id) {
      this.posteService.modifierPoste(this.posteSelectionne.id, payload).subscribe({
        next: () => {
          this.afficherSucces('Poste mis à jour avec succès !');
          this.router.navigate(['/postes']);
        },
        error: (err) => this.gererErreurs(err),
      });
    } else {
      this.posteService.creerPoste(payload).subscribe({
        next: () => {
          this.afficherSucces('Nouveau poste enregistré avec succès !');
          this.router.navigate(['/postes']);
        },
        error: (err) => this.gererErreurs(err),
      });
    }
  }



  demanderArchivage(poste: PosteModel): void {
    this.posteAActionnerId = poste.id;
    this.modalConfirmationConfig = {
      type: 'danger',
      titre: 'Archiver ce poste ?',
      message: `Vous êtes sur le point d'archiver le poste « ${poste.intitule} ». 
                Il sera désactivé et ne sera plus proposé aux employés.`,
      action: 'archiver',
    };
    this.afficherModalConfirmation = true;
    this.cdr.markForCheck();
  }

  demanderReactivation(poste: PosteModel): void {
    this.posteAActionnerId = poste.id;
    this.modalConfirmationConfig = {
      type: 'success',
      titre: 'Réactiver ce poste ?',
      message: `Le poste « ${poste.intitule} » sera réactivé et redeviendra disponible.`,
      action: 'reactiver',
    };
    this.afficherModalConfirmation = true;
    this.cdr.markForCheck();
  }

  confirmerAction(): void {
    if (!this.modalConfirmationConfig || !this.posteAActionnerId) return;

    const action = this.modalConfirmationConfig.action;
    const id = this.posteAActionnerId;

    this.fermerModalConfirmation();

    if (action === 'archiver') {
      this.posteService.archiverPoste(id).subscribe({
        next: () => {
          this.afficherSucces('Poste archivé avec succès.');
          this.chargerPostes();
        },
        error: (err) => this.gererErreurs(err),
      });
    } else if (action === 'reactiver') {
      this.posteService.reactiverPoste(id).subscribe({
        next: () => {
          this.afficherSucces('Poste réactivé avec succès.');
          this.chargerPostes();
        },
        error: (err) => this.gererErreurs(err),
      });
    }
  }

  fermerModalConfirmation(): void {
    this.afficherModalConfirmation = false;
    this.modalConfirmationConfig = null;
    this.posteAActionnerId = undefined;
    this.cdr.markForCheck();
  }


  getIconForNiveau(niveau: NiveauHierarchie | undefined): string {
    return this.niveaux.find((n) => n.value === niveau)?.icon || 'bi-person-fill';
  }

  getBadgeClassForNiveau(niveau: NiveauHierarchie | undefined): string {
    return this.niveaux.find((n) => n.value === niveau)?.badgeClass || '';
  }

  getLabelForNiveau(niveau: NiveauHierarchie | undefined): string {
    return this.niveaux.find((n) => n.value === niveau)?.label || niveau || '';
  }



  private afficherSucces(msg: string): void {
    clearTimeout(this._msgTimer);
    this.successMessage = msg;
    this.errorMessage = '';
    this.cdr.markForCheck();
    this._msgTimer = setTimeout(() => {
      this.successMessage = '';
      this.errorMessage = '';
      this.cdr.markForCheck();
    }, 3000);
  }

  private afficherErreur(msg: string): void {
    clearTimeout(this._msgTimer);
    this.errorMessage = msg;
    this.successMessage = '';
    this.cdr.markForCheck();
    this._msgTimer = setTimeout(() => {
      this.errorMessage = '';
      this.successMessage = '';
      this.cdr.markForCheck();
    }, 5000);
  }

  private gererErreurs(err: any): void {
    let messageErreur = 'Une erreur technique est survenue.';

    if (err?.error) {
      if (typeof err.error === 'string') {
        messageErreur = err.error;
      } else if (typeof err.error === 'object') {
        if (err.error.detail) {
          messageErreur = err.error.detail;
        } else if (err.error.message) {
          messageErreur = err.error.message;
        } else {
          const values = Object.values(err.error).flat();
          messageErreur = values.join(' ') || 'Données invalides.';
        }
      }
    } else if (err?.message) {
      messageErreur = err.message;
    }

    this.afficherErreur(messageErreur);
  }

  private initialiserFormulaire(): Partial<PosteModel> {
    return {
      intitule: '',
      description: '',
      niveau_hierarchie: 'JUNIOR',
      salaire_min: 0,
      salaire_max: 0,
      est_actif: true,
    };
  }
}
