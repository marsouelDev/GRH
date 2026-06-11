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
import { Subject, timer } from 'rxjs';
import { takeUntil } from 'rxjs/operators';

import { CongeService } from '../../../services/conges/conges';
import { AuthService, UtilisateurCourant } from '../../../services/auth/auth.service';
import { ThemeService } from '../../../services/Theme/theme-service';
import { CongeModel, TypeConge } from '../../../models/conge';

@Component({
  selector: 'app-conge',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './conges.html',
  styleUrls: ['./conges.css'],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class CongeComponent implements OnInit, OnDestroy {
  private congeService = inject(CongeService);
  private authService = inject(AuthService);
  private cdr = inject(ChangeDetectorRef);
  themeService = inject(ThemeService);
  private destroy$ = new Subject<void>();

  //  Timer unique pour les messages
  private messageTimer: any = null;

  user: UtilisateurCourant = this.authService.getCurrentUser();

  conges: CongeModel[] = [];
  message = '';
  errorMessage = '';
  chargement = false;
  modeAffichage: 'liste' | 'creation' | 'detail' | 'modification' = 'liste';
  congeSelectionne: CongeModel | null = null;
  filtreStatut: string = '';
  filtreEmployeId?: number;
  recherche = '';
  formulaire: Partial<CongeModel> = this.initialiserFormulaire();
  commentaireRefus = '';
  afficherModalRefus = false;
  congeARefuserId?: number;
  afficherModalConfirmation = false;
  modalConfirmationConfig: {
    titre: string;
    message: string;
    type: 'success' | 'warning' | 'danger';
    action: () => void;
  } | null = null;

  readonly typesConge: { value: TypeConge; label: string }[] = [
    { value: 'ANNUEL', label: 'Congé annuel' },
    { value: 'MALADIE', label: 'Congé maladie' },
    { value: 'MATERNITE', label: 'Congé maternité' },
    { value: 'SANS_SOLDE', label: 'Congé sans solde' },
    { value: 'AUTRE', label: 'Autre' },
  ];

  ngOnInit(): void {
    this.loadConges();
  }

  ngOnDestroy(): void {
    this.destroy$.next();
    this.destroy$.complete();
    //  Nettoyer le timer
    if (this.messageTimer) {
      clearTimeout(this.messageTimer);
    }
  }

  get isManager(): boolean {
    return this.user?.role === 'ADMIN' || this.user?.role === 'RH';
  }

  get isRH(): boolean {
    return this.user?.role === 'RH';
  }

  get isAdmin(): boolean {
    return this.user?.role === 'ADMIN';
  }

  get isEmploye(): boolean {
    return this.user?.role === 'EMPLOYE';
  }

  get isDarkMode(): boolean {
    return this.themeService.isDarkMode();
  }

  get nomAffiche(): string {
    return this.user?.prenom || this.user?.nom || this.user?.email || 'Utilisateur';
  }

  tronquerMotif(motif?: string | null, maxLength: number = 30): string {
    if (!motif) return '—';
    return motif.length > maxLength ? motif.substring(0, maxLength) + '…' : motif;
  }

  get congesFiltres(): CongeModel[] {
    return this.conges.filter((c) => {
      const terme = this.recherche.toLowerCase().trim();
      const matchTexte =
        !terme ||
        (c.employe_nom || '').toLowerCase().includes(terme) ||
        (c.motif || '').toLowerCase().includes(terme) ||
        (c.type_label || '').toLowerCase().includes(terme);
      const matchStatut = !this.filtreStatut || c.statut === this.filtreStatut;
      return matchTexte && matchStatut;
    });
  }

  get nbEnAttente(): number {
    return this.conges.filter((c) => c.statut === 'EN_ATTENTE').length;
  }

  get nbApprouves(): number {
    return this.conges.filter((c) => c.statut === 'APPROUVE').length;
  }

  get nbRefuses(): number {
    return this.conges.filter((c) => c.statut === 'REFUSE').length;
  }

  get nbAnnules(): number {
    return this.conges.filter((c) => c.statut === 'ANNULE').length;
  }

  loadConges(): void {
    this.errorMessage = '';
    this.chargement = true;
    this.cdr.markForCheck();

    const filtres = this.isManager
      ? { statut: this.filtreStatut || undefined, employeId: this.filtreEmployeId }
      : {};

    this.congeService.getConges(filtres).subscribe({
      next: (data) => {
        this.conges = data;
        this.chargement = false;
        this.cdr.markForCheck();
      },
      error: (err) => {
        this.errorMessage = err?.error?.detail || 'Erreur lors du chargement des congés.';
        this.chargement = false;
        this.masquerMessages();
        this.cdr.markForCheck();
      },
    });
  }

  creerConge(): void {
    if (this.isManager) return;

    if (!this.formulaire.date_debut || !this.formulaire.date_fin) {
      this.errorMessage = ' Veuillez remplir les dates de début et de fin.';
      this.cdr.markForCheck();
      this.masquerMessages(4000);
      return;
    }

    if (new Date(this.formulaire.date_debut) > new Date(this.formulaire.date_fin)) {
      this.errorMessage = ' La date de début doit être antérieure à la date de fin.';
      this.cdr.markForCheck();
      this.masquerMessages(4000);
      return;
    }

    this.chargement = true;
    this.cdr.markForCheck();

    this.congeService.creerConge(this.formulaire).subscribe({
      next: () => {
        this.message = ' Demande de congé soumise avec succès !';
        this.formulaire = this.initialiserFormulaire();
        this.cdr.markForCheck();
        this.loadConges();
        this.modeAffichage = 'liste';
        this.masquerMessages(5000);
      },
      error: (err) => {
        this.errorMessage =
          err?.error?.detail ||
          Object.values(err?.error || {})
            .flat()
            .join(' ') ||
          ' Impossible de soumettre la demande.';
        this.chargement = false;
        this.cdr.markForCheck();
        this.masquerMessages(5000);
      },
    });
  }

  ouvrirModification(conge: CongeModel): void {
    this.congeSelectionne = { ...conge };
    this.formulaire = {
      type_conge: conge.type_conge,
      date_debut: conge.date_debut,
      date_fin: conge.date_fin,
      motif: conge.motif,
    };
    this.modeAffichage = 'modification';
    this.cdr.markForCheck();
  }

  sauvegarderModification(): void {
    if (!this.congeSelectionne?.id) return;

    if (!this.formulaire.date_debut || !this.formulaire.date_fin) {
      this.errorMessage = ' Veuillez remplir les dates de début et de fin.';
      this.cdr.markForCheck();
      this.masquerMessages(4000);
      return;
    }

    if (new Date(this.formulaire.date_debut) > new Date(this.formulaire.date_fin)) {
      this.errorMessage = ' La date de début doit être antérieure à la date de fin.';
      this.cdr.markForCheck();
      this.masquerMessages(4000);
      return;
    }

    this.chargement = true;
    this.cdr.markForCheck();

    this.congeService.modifierConge(this.congeSelectionne.id, this.formulaire).subscribe({
      next: () => {
        this.message = ' Congé modifié avec succès.';
        this.cdr.markForCheck();
        this.loadConges();
        this.modeAffichage = 'liste';
        this.masquerMessages(5000);
      },
      error: (err) => {
        this.errorMessage = err?.error?.detail || ' Impossible de modifier ce congé.';
        this.chargement = false;
        this.cdr.markForCheck();
        this.masquerMessages(5000);
      },
    });
  }

  voirDetail(conge: CongeModel): void {
    if (!conge.id) return;

    this.chargement = true;
    this.cdr.markForCheck();

    this.congeService.getConge(conge.id).subscribe({
      next: (data) => {
        this.congeSelectionne = data;
        this.modeAffichage = 'detail';
        this.chargement = false;
        this.cdr.markForCheck();
      },
      error: (err) => {
        this.errorMessage = err?.error?.detail || ' Impossible de charger ce congé.';
        this.chargement = false;
        this.masquerMessages();
        this.cdr.markForCheck();
      },
    });
  }

  demanderAnnulation(id: number): void {
    this.modalConfirmationConfig = {
      titre: 'Annuler le congé',
      message:
        'Êtes-vous sûr de vouloir annuler cette demande de congé ? Cette action est irréversible.',
      type: 'warning',
      action: () => this.executerAnnulation(id),
    };
    this.afficherModalConfirmation = true;
    this.cdr.markForCheck();
  }

  private executerAnnulation(id: number): void {
    this.chargement = true;
    this.cdr.markForCheck();

    this.congeService.annulerConge(id).subscribe({
      next: (res) => {
        this.message = res?.detail || ' Congé annulé avec succès.';
        console.log(' Toast annulation:', this.message);
        this.cdr.markForCheck();
        this.loadConges();
        if (this.modeAffichage !== 'liste') this.modeAffichage = 'liste';
        this.masquerMessages(5000);
      },
      error: (err) => {
        this.errorMessage = err?.error?.detail || " Impossible d'annuler ce congé.";
        this.chargement = false;
        this.cdr.markForCheck();
        this.masquerMessages(5000);
      },
    });
  }

  demanderApprobation(id: number): void {
    if (!this.isRH) return;

    this.modalConfirmationConfig = {
      titre: 'Approuver le congé',
      message: 'Êtes-vous sûr de vouloir approuver cette demande de congé ?',
      type: 'success',
      action: () => this.executerApprobation(id),
    };
    this.afficherModalConfirmation = true;
    this.cdr.markForCheck();
  }

  private executerApprobation(id: number): void {
    this.chargement = true;
    this.cdr.markForCheck();

    this.congeService.approuverConge(id).subscribe({
      next: (res) => {
        this.message = res?.detail || ' Congé approuvé avec succès !';
        console.log(' Toast approbation:', this.message);
        this.cdr.markForCheck();
        this.loadConges();
        if (this.modeAffichage === 'detail') this.voirDetail({ id } as CongeModel);
        this.masquerMessages(5000);
      },
      error: (err) => {
        this.errorMessage = err?.error?.detail || " Impossible d'approuver ce congé.";
        this.chargement = false;
        this.cdr.markForCheck();
        this.masquerMessages(5000);
      },
    });
  }

  ouvrirModalRefus(id: number): void {
    if (!this.isRH) return;

    this.congeARefuserId = id;
    this.commentaireRefus = '';
    this.afficherModalRefus = true;
    this.cdr.markForCheck();
  }

  confirmerRefus(): void {
    if (!this.congeARefuserId || !this.isRH) return;

    this.chargement = true;
    this.cdr.markForCheck();

    this.congeService
      .refuserConge(this.congeARefuserId, { commentaire: this.commentaireRefus })
      .subscribe({
        next: (res) => {
          this.message = res?.detail || ' Congé refusé avec succès.';
          console.log(' Toast refus:', this.message);
          this.annulerModalRefus();
          this.cdr.markForCheck();
          this.loadConges();
          if (this.modeAffichage === 'detail') this.modeAffichage = 'liste';
          this.masquerMessages(5000);
        },
        error: (err) => {
          this.errorMessage = err?.error?.detail || '❌ Impossible de refuser ce congé.';
          this.chargement = false;
          this.cdr.markForCheck();
          this.masquerMessages(5000);
        },
      });
  }

  annulerModalRefus(): void {
    this.afficherModalRefus = false;
    this.congeARefuserId = undefined;
    this.commentaireRefus = '';
    this.cdr.markForCheck();
  }

  confirmerAction(): void {
    if (this.modalConfirmationConfig?.action) {
      this.modalConfirmationConfig.action();
    }
    this.fermerModalConfirmation();
  }

  fermerModalConfirmation(): void {
    this.afficherModalConfirmation = false;
    this.modalConfirmationConfig = null;
    this.cdr.markForCheck();
  }

  retourListe(): void {
    this.modeAffichage = 'liste';
    this.congeSelectionne = null;
    this.formulaire = this.initialiserFormulaire();
    this.cdr.markForCheck();
  }

  peutModifier(conge: CongeModel): boolean {
    if (this.isManager) return true;
    return this.isEmploye && conge.statut === 'EN_ATTENTE';
  }

  peutAnnuler(conge: CongeModel): boolean {
    if (!conge || conge.statut === 'ANNULE') return false;
    if (this.isManager) return true;
    return this.isEmploye && conge.statut === 'EN_ATTENTE';
  }

  private initialiserFormulaire(): Partial<CongeModel> {
    return {
      type_conge: 'ANNUEL',
      date_debut: '',
      date_fin: '',
      motif: '',
    };
  }

  //  Méthode corrigée avec timer unique
  private masquerMessages(delai: number = 5000): void {
    // Annuler le timer précédent
    if (this.messageTimer) {
      clearTimeout(this.messageTimer);
      this.messageTimer = null;
    }

    this.messageTimer = setTimeout(() => {
      this.message = '';
      this.errorMessage = '';
      this.messageTimer = null;
      this.cdr.markForCheck();
    }, delai);
  }
}
