import {
  ChangeDetectionStrategy,
  ChangeDetectorRef,
  Component,
  inject,
  NgZone,
  OnDestroy,
  OnInit,
} from '@angular/core';
import { CommonModule, DatePipe } from '@angular/common';
import { FormsModule } from '@angular/forms';

import { AuthService, UtilisateurCourant } from '../../../services/auth/auth.service';
import { RapportService } from '../../../services/rapport/rapport';
import { ThemeService } from '../../../services/Theme/theme-service';
import { RapportModel, TypeRapport } from '../../../models/rapport';
import { RapportTypeCountPipe } from '../../../pipes/rapport-type-count-pipe';

export interface DonneeEntry {
  cle: string;
  valeur: any;
  isNested: boolean;
  isArray: boolean;
}

@Component({
  selector: 'app-rapport',
  standalone: true,
  imports: [CommonModule, FormsModule, RapportTypeCountPipe],
  templateUrl: './rapport.html',
  styleUrl: 'rapport.css',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class Rapport implements OnInit, OnDestroy {
  private rapportService = inject(RapportService);
  private authService = inject(AuthService);
  private cdr = inject(ChangeDetectorRef);
  private ngZone = inject(NgZone);
  themeService = inject(ThemeService);
  user: UtilisateurCourant = this.authService.getCurrentUser();
  rapports: RapportModel[] = [];
  rapportSelectionne: RapportModel | null = null;
  message = '';
  errorMessage = '';
  chargement = false;
  modeAffichage: 'liste' | 'creation' | 'detail' = 'liste';
  recherche = '';
  filtreType = '';
  formulaire: Partial<RapportModel> = this.initialiserFormulaire();
  private messageTimer: ReturnType<typeof setTimeout> | null = null;
  private errorTimer: ReturnType<typeof setTimeout> | null = null;

  modalSuppression: { visible: boolean; id: number | null; titre: string } = {
    visible: false,
    id: null,
    titre: '',
  };

  readonly typesRapport: { value: TypeRapport; label: string; icon: string }[] = [
    { value: 'EFFECTIFS', label: 'Effectifs', icon: 'bi-people-fill' },
    { value: 'PRESENCES', label: 'Présences', icon: 'bi-clock-history' },
    { value: 'ABSENCES', label: 'Absences', icon: 'bi-x-circle-fill' },
    { value: 'CONGES', label: 'Congés', icon: 'bi-calendar2-week-fill' },
    { value: 'JUSTIFICATIONS', label: 'Justifications', icon: 'bi-file-earmark-text-fill' },
    { value: 'SALAIRES', label: 'Salaires', icon: 'bi-cash-stack' },
    { value: 'MENSUEL', label: 'Mensuel complet', icon: 'bi-bar-chart-fill' },
  ];

  ngOnInit(): void {
    this.user = this.authService.getCurrentUser();
    this.chargerRapports();
    if (this.themeService.isDarkMode()) {
      document.documentElement.classList.add('dark');
    }
  }

  ngOnDestroy(): void {
    this._clearTimers();
  }

  get isRH(): boolean {
    return (this.user?.role ?? '').toUpperCase() === 'RH';
  }
  get isAdmin(): boolean {
    return (this.user?.role ?? '').toUpperCase() === 'ADMIN';
  }
  get isManager(): boolean {
    return this.isRH || this.isAdmin;
  }
  get isDarkMode(): boolean {
    return this.themeService.isDarkMode();
  }

  get rapportsFiltres(): RapportModel[] {
    const terme = this.recherche.toLowerCase().trim();
    return this.rapports.filter((r) => {
      const matchTexte =
        !terme ||
        (r.titre || '').toLowerCase().includes(terme) ||
        (r.type_label || '').toLowerCase().includes(terme) ||
        (r.genere_par_nom || '').toLowerCase().includes(terme);
      const matchType = !this.filtreType || r.type_rapport === this.filtreType;
      return matchTexte && matchType;
    });
  }

  getLabelType(type: string): string {
    return this.typesRapport.find((t) => t.value === type)?.label ?? type;
  }

  getIconType(type: string): string {
    return this.typesRapport.find((t) => t.value === type)?.icon ?? 'bi-file-earmark';
  }

  getDonneesEntries(donnees: Record<string, any> | null | undefined): DonneeEntry[] {
    if (!donnees) return [];
    return Object.entries(donnees).map(([cle, valeur]) => ({
      cle: cle.replace(/_/g, ' '),
      valeur,
      isNested: !Array.isArray(valeur) && valeur !== null && typeof valeur === 'object',
      isArray: Array.isArray(valeur),
    }));
  }

  getNestedEntries(valeur: Record<string, any>): DonneeEntry[] {
    return this.getDonneesEntries(valeur);
  }

  formatListItem(item: any): { label: string; valeur: any } {
    if (typeof item !== 'object' || item === null) {
      return { label: '—', valeur: item };
    }
    if ('role' in item || 'type_conge' in item) {
      const label = item.role ?? item.type_conge ?? '—';
      return { label, valeur: item.total ?? item.nb ?? '—' };
    }
    if ('employe__nom' in item || 'employe__prenom' in item) {
      const nom = item['employe__nom'] ?? '';
      const prenom = item['employe__prenom'] ?? '';
      const label = `${nom} ${prenom}`.trim() || '—';
      const valeur =
        item.nb_absences ??
        item.nb_conges ??
        item.nb_justifications ??
        item.nb_presents ??
        item.total ??
        '—';
      return { label, valeur };
    }
    const entries = Object.entries(item);
    if (entries.length === 0) {
      return { label: '—', valeur: '—' };
    }
    const [firstKey, firstVal] = entries[0];
    return { label: String(firstKey), valeur: firstVal };
  }

  chargerRapports(): void {
    this.chargement = true;
    this.cdr.markForCheck();
    this.rapportService.getRapports(this.filtreType || undefined).subscribe({
      next: (data) => {
        this.rapports = data;
        this.chargement = false;
        this.cdr.markForCheck();
      },
      error: (err) => {
        this.chargement = false;
        this.afficherErreur(err?.error?.detail || 'Erreur lors du chargement.');
        this.cdr.markForCheck();
      },
    });
  }

  creerRapport(): void {
    if (!this.formulaire.titre?.trim() || !this.formulaire.type_rapport) {
      this.afficherErreur('Le titre et le type sont obligatoires.');
      return;
    }
    this.chargement = true;
    this.cdr.markForCheck();
    this.rapportService.creerRapport(this.formulaire).subscribe({
      next: (data) => {
        this.rapports.unshift(data);
        this.formulaire = this.initialiserFormulaire();
        this.modeAffichage = 'liste';
        this.chargement = false;
        this.afficherSucces('Rapport généré avec succès.');
        this.cdr.markForCheck();
      },
      error: (err) => {
        this.chargement = false;
        this.afficherErreur(err?.error?.detail || 'Impossible de créer le rapport.');
        this.cdr.markForCheck();
      },
    });
  }

  voirDetail(rapport: RapportModel): void {
    if (!rapport.id) return;
    this.chargement = true;
    this.cdr.markForCheck();
    this.rapportService.getRapport(rapport.id).subscribe({
      next: (data) => {
        this.rapportSelectionne = data;
        this.modeAffichage = 'detail';
        this.chargement = false;
        this.cdr.markForCheck();
      },
      error: (err) => {
        this.chargement = false;
        this.afficherErreur(err?.error?.detail || 'Impossible de charger le rapport.');
        this.cdr.markForCheck();
      },
    });
  }

  regenerer(id: number): void {
    this.chargement = true;
    this.cdr.markForCheck();
    this.rapportService.regenerer(id).subscribe({
      next: (data) => {
        this.rapportSelectionne = data;
        const idx = this.rapports.findIndex((r) => r.id === id);
        if (idx !== -1) this.rapports[idx] = data;
        this.chargement = false;
        this.afficherSucces('Rapport regénéré avec succès.');
        this.cdr.markForCheck();
      },
      error: (err) => {
        this.chargement = false;
        this.afficherErreur(err?.error?.detail || 'Erreur lors de la regénération.');
        this.cdr.markForCheck();
      },
    });
  }

  ouvrirModalSuppression(id: number, titre: string): void {
    this.modalSuppression = {
      visible: true,
      id,
      titre,
    };
    this.cdr.markForCheck();
  }

  annulerSuppression(): void {
    this.modalSuppression = { visible: false, id: null, titre: '' };
    this.cdr.markForCheck();
  }

  confirmerSuppression(): void {
    const id = this.modalSuppression.id;
    if (!id) return;

    this.chargement = true;
    this.cdr.markForCheck();

    this.rapportService.supprimer(id).subscribe({
      next: () => {
        this.rapports = this.rapports.filter((r) => r.id !== id);
        if (this.modeAffichage === 'detail') this.modeAffichage = 'liste';
        this.modalSuppression = { visible: false, id: null, titre: '' };
        this.chargement = false;
        this.afficherSucces('Rapport supprimé définitivement.');
        this.cdr.markForCheck();
      },
      error: (err) => {
        this.chargement = false;
        this.modalSuppression = { visible: false, id: null, titre: '' };
        this.afficherErreur(err?.error?.detail || 'Impossible de supprimer le rapport.');
        this.cdr.markForCheck();
      },
    });
  }

  exporterExcel(id: number): void {
    this.chargement = true;
    this.rapportService.exporterExcel(id).subscribe({
      next: (blob) => {
        this._telechargerFichier(
          blob,
          `rapport_${id}.xlsx`,
          'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        );
        this.chargement = false;
        this.afficherSucces('Export Excel réussi.');
      },
      error: (err) => {
        this.chargement = false;
        this.afficherErreur("Erreur lors de l'export Excel.");
      },
    });
  }

  exporterPdf(id: number): void {
    this.chargement = true;
    this.rapportService.exporterPdf(id).subscribe({
      next: (blob) => {
        this._telechargerFichier(blob, `rapport_${id}.pdf`, 'application/pdf');
        this.chargement = false;
        this.afficherSucces('Export PDF réussi.');
      },
      error: (err) => {
        this.chargement = false;
        this.afficherErreur("Erreur lors de l'export PDF.");
      },
    });
  }

  private _telechargerFichier(blob: Blob, nomFichier: string, typeMime: string): void {
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.style.display = 'none';
    a.href = url;
    a.download = nomFichier;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    window.URL.revokeObjectURL(url);
  }

  retourListe(): void {
    this.modeAffichage = 'liste';
    this.rapportSelectionne = null;
    this.formulaire = this.initialiserFormulaire();
  }

  dismissNotif(): void {
    this.message = '';
    this.errorMessage = '';
    this._clearTimers();
    this.cdr.markForCheck();
  }

  toggleFiltre(type: string): void {
    this.filtreType = this.filtreType === type ? '' : type;
    this.chargerRapports();
  }

  resetFiltres(): void {
    this.recherche = '';
    this.filtreType = '';
    this.chargerRapports();
  }

  private initialiserFormulaire(): Partial<RapportModel> {
    return {
      titre: '',
      type_rapport: 'PRESENCES',
      description: '',
      date_debut: null,
      date_fin: null,
    };
  }

  private afficherSucces(msg: string): void {
    if (this.messageTimer) clearTimeout(this.messageTimer);
    this.message = msg;
    this.errorMessage = '';
    this.cdr.markForCheck();
    this.ngZone.run(() => {
      this.messageTimer = setTimeout(() => {
        this.message = '';
        this.cdr.markForCheck();
      }, 4000);
    });
  }

  private afficherErreur(msg: string): void {
    if (this.errorTimer) clearTimeout(this.errorTimer);
    this.errorMessage = msg;
    this.message = '';
    this.cdr.markForCheck();
    this.ngZone.run(() => {
      this.errorTimer = setTimeout(() => {
        this.errorMessage = '';
        this.cdr.markForCheck();
      }, 5000);
    });
  }

  private _clearTimers(): void {
    if (this.messageTimer) clearTimeout(this.messageTimer);
    if (this.errorTimer) clearTimeout(this.errorTimer);
  }
}
