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
import { ActivatedRoute } from '@angular/router';
import { SafePipe } from '../../../pipes/safe-pipe';
import { AuthService, UtilisateurCourant } from '../../../services/auth/auth.service';
import { ThemeService } from '../../../services/Theme/theme-service';
import { PresenceService } from '../../../services/presence/presence';
import { JustificationService } from '../../../services/justification/justification';
import { Justification, NouvelleJustif } from '../../../models/justification';
import { Presence } from '../../../models/presences';
import { environment } from '../../../../environments/environments';

@Component({
  selector: 'app-justification',
  standalone: true,
  imports: [CommonModule, FormsModule, SafePipe],
  templateUrl: './justification.html',
  styleUrl: './justification.css',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class JustificationComponent implements OnInit, OnDestroy {

  private readonly authService = inject(AuthService);
  private readonly themeService = inject(ThemeService);
  private readonly presenceService = inject(PresenceService);
  private readonly justifService = inject(JustificationService);
  private readonly route = inject(ActivatedRoute);
  private readonly cdr = inject(ChangeDetectorRef);
  private readonly backendUrl = environment.apiUrl || 'http://localhost:8000';

  // ── État principal ────────────────────────────────────────
  user: UtilisateurCourant = this.authService.getCurrentUser();
  justifications: Justification[] = [];
  presencesDisponibles: Presence[] = [];
  justificationSelectionnee: Justification | null = null;
  chargement = false;
  afficherFormulaireCreation = false;
  message = '';
  errorMessage = '';
  private _timer?: ReturnType<typeof setTimeout>;
  filtres = {
    statut: '',
    type_justif: '',
    employe: undefined as number | undefined,
  };
  recherche = '';
  nouvelleJustif: NouvelleJustif = this.viderFormulaire();
  fichierSelectionne: File | null = null;
  commentaireAction = '';
  docUrl: string | null = null;
  docType: 'pdf' | 'image' | 'word' | 'other' = 'other';
  docLoaded = false;
  docError = false;
  viewerUrl: string | null = null;
  afficherModalSuppression = false;
  justificationASupprimer: Justification | null = null;
  chargementSuppression = false;

  ngOnInit(): void {
    this.user = this.authService.getCurrentUser();
    this.chargerJustifications();
    if (this.isEmploye) this.chargerPresencesDisponibles();
    this.gererPreRemplissagePresence();
  }

  ngOnDestroy(): void {
    this.nettoyerTimer();
  }

  get userRole(): string {
    return (this.user?.role ?? '').toUpperCase();
  }
  get isEmploye(): boolean {
    return this.userRole === 'EMPLOYE';
  }
  get isManager(): boolean {
    return ['ADMIN', 'RH'].includes(this.userRole);
  }
  get isRH(): boolean {
    return this.userRole === 'RH';
  }
  get isDarkMode(): boolean {
    return this.themeService.isDarkMode();
  }

  get justificationsFiltrees(): Justification[] {
    const terme = this.recherche.toLowerCase().trim();
    return this.justifications.filter((j) => {
      const matchTexte =
        !terme ||
        (j.employe_nom || '').toLowerCase().includes(terme) ||
        (j.motif || '').toLowerCase().includes(terme);
      const matchStatut = !this.filtres.statut || j.statut === this.filtres.statut;
      const matchType = !this.filtres.type_justif || j.type_justif === this.filtres.type_justif;
      return matchTexte && matchStatut && matchType;
    });
  }

  get nbEnAttente(): number {
    return this.justifications.filter((j) => j.statut === 'EN_ATTENTE').length;
  }
  get nbValidees(): number {
    return this.justifications.filter((j) => j.statut === 'VALIDEE').length;
  }
  get nbRefusees(): number {
    return this.justifications.filter((j) => j.statut === 'REFUSEE').length;
  }

  toggleTheme(): void {
    this.themeService.toggleTheme();
  }

  reinitialiserFiltres(): void {
    this.filtres = { statut: '', type_justif: '', employe: undefined };
    this.recherche = '';
    this.chargerJustifications();
  }

  ouvrirArbitrage(justification: Justification): void {
    this.justificationSelectionnee = justification;
    this.commentaireAction = '';
    this.cdr.markForCheck();
  }

  fermerModal(): void {
    this.justificationSelectionnee = null;
    this.commentaireAction = '';
    this.cdr.markForCheck();
  }

  dismissModal(): void {
    this.nettoyerMessages();
  }

  

  /** Ouvre le document selon son type */
  voirDocument(url: string): void {
    if (!url) {
      this.afficherErreur('Aucun document disponible');
      return;
    }

    const absoluteUrl = this.construireUrlAbsolue(url);

    const urlLower = absoluteUrl.toLowerCase();

    // Détection du type de fichier
    if (urlLower.match(/\.(png|jpg|jpeg|gif|webp|bmp|svg)$/)) {
      this.docType = 'image';
      this.docUrl = absoluteUrl;
      this.viewerUrl = null;
      this.docLoaded = false;
      this.docError = false;
      this.cdr.markForCheck();
    } else if (urlLower.endsWith('.pdf')) {
      this.docType = 'pdf';
      this.docUrl = absoluteUrl;
      this.viewerUrl = null;
      this.docLoaded = false;
      this.docError = false;
      this.cdr.markForCheck();

      // Ouvrir automatiquement dans un nouvel onglet
      setTimeout(() => {
        window.open(absoluteUrl, '_blank');
      }, 300);
    } else if (urlLower.match(/\.(doc|docx)$/)) {
      // 👇 WORD : utiliser Google Docs Viewer
      this.docType = 'word';
      this.docUrl = absoluteUrl;
      this.viewerUrl = `https://docs.google.com/viewer?url=${encodeURIComponent(absoluteUrl)}&embedded=true`;
      this.docLoaded = false;
      this.docError = false;
      this.cdr.markForCheck();
    } else {
      this.docType = 'other';
      this.docUrl = absoluteUrl;
      this.viewerUrl = null;
      this.cdr.markForCheck();

      setTimeout(() => {
        window.open(absoluteUrl, '_blank');
      }, 300);
    }
  }

  ouvrirDansNouvelOnglet(): void {
    if (this.docUrl) {
      window.open(this.docUrl, '_blank');
    }
  }

  private construireUrlAbsolue(url: string): string {
    if (url.startsWith('http')) return url;
    if (url.startsWith('/')) return `${this.backendUrl}${url}`;
    return `${this.backendUrl}/${url}`;
  }

  fermerDocument(): void {
    this.docUrl = null;
    this.docType = 'other';
    this.viewerUrl = null;
    this.docLoaded = false;
    this.docError = false;
    this.cdr.markForCheck();
  }

  onDocLoaded(): void {
    this.docLoaded = true;
    this.docError = false;
    this.cdr.markForCheck();
  }

  /** Callback en cas d'erreur */
  onDocError(error: any): void {
    this.docError = true;
    this.docLoaded = false;
    this.cdr.markForCheck();
  }


  confirmerSuppression(justification: Justification): void {
    this.justificationASupprimer = justification;
    this.afficherModalSuppression = true;
    this.cdr.markForCheck();
  }

  annulerSuppression(): void {
    this.afficherModalSuppression = false;
    this.justificationASupprimer = null;
    this.chargementSuppression = false;
    this.cdr.markForCheck();
  }

  executerSuppression(): void {
    if (!this.justificationASupprimer?.id) return;

    this.chargementSuppression = true;
    this.cdr.markForCheck();

    this.justifService.supprimerJustification(this.justificationASupprimer.id).subscribe({
      next: () => {
        this.afficherSucces('Justification supprimée avec succès.');
        this.annulerSuppression();
        this.chargerJustifications();
        if (this.isEmploye) this.chargerPresencesDisponibles();
        this.cdr.markForCheck();
      },
      error: (err) => {
        this.afficherErreur(err?.error?.detail || 'Erreur lors de la suppression.');
        this.chargementSuppression = false;
        this.cdr.markForCheck();
      },
    });
  }

 
  validerDossier(id: number): void {
    if (!this.isRH) return;
    this.chargement = true;
    this.cdr.markForCheck();

    this.justifService.valider(id, this.commentaireAction).subscribe({
      next: (res) => {
        this.afficherSucces(res?.detail || 'Validée.');
        this.fermerModal();
        this.chargerJustifications();
        this.cdr.markForCheck();
      },
      error: (err) => {
        this.afficherErreur(err?.error?.detail || 'Erreur validation.');
        this.chargement = false;
        this.cdr.markForCheck();
      },
      complete: () => {
        this.chargement = false;
        this.cdr.markForCheck();
      },
    });
  }

  rejeterDossier(id: number): void {
    if (!this.isRH) return;
    this.chargement = true;
    this.cdr.markForCheck();

    this.justifService.rejeter(id, this.commentaireAction).subscribe({
      next: (res) => {
        this.afficherSucces(res?.detail || 'Rejetée.');
        this.fermerModal();
        this.chargerJustifications();
        this.cdr.markForCheck();
      },
      error: (err) => {
        this.afficherErreur(err?.error?.detail || 'Erreur refus.');
        this.chargement = false;
        this.cdr.markForCheck();
      },
      complete: () => {
        this.chargement = false;
        this.cdr.markForCheck();
      },
    });
  }

  soumettreDemande(): void {
    if (!this.validerFormulaire()) return;
    const formData = this.construireFormData();

    this.chargement = true;
    this.cdr.markForCheck();

    this.justifService.creerJustification(formData).subscribe({
      next: () => {
        this.afficherSucces('Soumise avec succès.');
        this.reinitialiserFormulaire();
        this.chargerJustifications();
        this.chargerPresencesDisponibles();
        this.cdr.markForCheck();
      },
      error: (err) => {
        this.afficherErreur(this.extraireMessageErreur(err));
        this.chargement = false;
        this.cdr.markForCheck();
      },
      complete: () => {
        this.chargement = false;
        this.cdr.markForCheck();
      },
    });
  }

  onFileSelected(event: Event): void {
    const input = event.target as HTMLInputElement;
    const file = input.files?.[0];
    if (!file) return;

    const typesValides = [
      'application/pdf',
      'image/jpeg',
      'image/png',
      'application/msword',
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    ];

    if (typesValides.includes(file.type) && file.size <= 5 * 1024 * 1024) {
      this.fichierSelectionne = file;
      this.cdr.markForCheck();
    } else {
      this.afficherErreur('Fichier non valide (PDF, JPG, PNG, DOC — max 5 Mo)');
      input.value = '';
    }
  }


  calculateProgress(value: string | undefined | null, multiplier = 20, max = 100): number {
    const length = typeof value === 'string' ? value.length : 0;
    return Math.min(max, length * multiplier);
  }

  getPresenceIdValue(presence: Presence): number | null {
    return presence.id && presence.id > 0 ? presence.id : null;
  }

  trackById(_: number, item: { id: number }): number {
    return item.id;
  }

  tronquerMotif(motif: string | undefined, max = 50): string {
    return !motif ? '—' : motif.length > max ? motif.slice(0, max) + '…' : motif;
  }


  chargerJustifications(): void {
    this.chargement = true;
    this.cdr.markForCheck();

    const filtres = this.isManager ? { ...this.filtres } : {};
    this.justifService.getJustifications(filtres).subscribe({
      next: (data) => {
        this.justifications = data ?? [];
        this.chargement = false;
        this.cdr.markForCheck();
      },
      error: (err) => {
        this.chargement = false;
        this.afficherErreur(err?.error?.detail || 'Erreur chargement.');
        this.cdr.markForCheck();
      },
    });
  }

  chargerPresencesDisponibles(): void {
    if (!this.isEmploye) return;
    this.cdr.markForCheck();

    this.presenceService.getPresences().subscribe({
      next: (data) => {
        this.presencesDisponibles = data.filter(
          (p) =>
            (p.statut === 'ABSENT' || p.statut === 'RETARD') &&
            p.id != null &&
            p.id > 0 &&
            !p.justifie,
        );
        this.cdr.markForCheck();
      },
      error: (err) => {
        this.afficherErreur(err?.error?.detail || 'Erreur présences.');
        this.cdr.markForCheck();
      },
    });
  }

  gererPreRemplissagePresence(): void {
    const presenceId = this.route.snapshot.queryParamMap.get('presenceId');
    if (presenceId && this.isEmploye) {
      const parsed = Number(presenceId);
      if (parsed > 0) {
        this.nouvelleJustif.presence = parsed;
        this.afficherFormulaireCreation = true;
        this.cdr.markForCheck();
      }
    }
  }

 
  validerFormulaire(): boolean {
    if (!this.nouvelleJustif.presence || this.nouvelleJustif.presence <= 0) {
      this.afficherErreur(
        this.presencesDisponibles.length === 0
          ? 'Aucune absence/retard à justifier.'
          : 'Sélectionnez une présence.',
      );
      return false;
    }
    if (!this.nouvelleJustif.type_justif) {
      this.afficherErreur('Choisissez un type.');
      return false;
    }
    if ((this.nouvelleJustif.motif || '').trim().length < 5) {
      this.afficherErreur('Le motif doit contenir au moins 5 caractères.');
      return false;
    }
    return true;
  }

  construireFormData(): FormData {
    const formData = new FormData();
    formData.append('presence', String(this.nouvelleJustif.presence));
    formData.append('type_justif', this.nouvelleJustif.type_justif!);
    formData.append('motif', (this.nouvelleJustif.motif || '').trim());

    if (this.fichierSelectionne) {
      formData.append('document', this.fichierSelectionne, this.fichierSelectionne.name);
    }

    return formData;
  }

  extraireMessageErreur(err: any): string {
    return (
      err?.error?.detail ||
      Object.entries(err?.error || {})
        .map(([k, v]) => `${k} : ${(v as string[]).join(', ')}`)
        .join(' | ') ||
      'Erreur soumission.'
    );
  }

  reinitialiserFormulaire(): void {
    this.afficherFormulaireCreation = false;
    this.nouvelleJustif = this.viderFormulaire();
    this.fichierSelectionne = null;
    this.cdr.markForCheck();
  }

  viderFormulaire(): NouvelleJustif {
    return { presence: null, type_justif: null, motif: '' };
  }


  afficherSucces(message: string): void {
    this.nettoyerTimer();
    this.message = message;
    this.errorMessage = '';
    this.cdr.markForCheck();
    this._timer = setTimeout(() => {
      this.message = '';
      this.cdr.markForCheck();
    }, 3000);
  }

  afficherErreur(message: string): void {
    this.nettoyerTimer();
    this.errorMessage = message;
    this.message = '';
    this.cdr.markForCheck();
    this._timer = setTimeout(() => {
      this.errorMessage = '';
      this.cdr.markForCheck();
    }, 3000);
  }

  nettoyerMessages(): void {
    this.message = '';
    this.errorMessage = '';
    this.cdr.markForCheck();
  }

  nettoyerTimer(): void {
    if (this._timer) {
      clearTimeout(this._timer);
      this._timer = undefined;
    }
  }
}
