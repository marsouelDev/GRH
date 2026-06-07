import {
  Component,
  OnInit,
  inject,
  ChangeDetectorRef,
  ChangeDetectionStrategy,
} from '@angular/core';
import { FormsModule, NgForm } from '@angular/forms';
import { CommonModule } from '@angular/common';
import { Router } from '@angular/router';

import { ContratService } from '../../../services/contrats/contrats-services';
import { EmployeeService } from '../../../services/employee/employee-service';
import { PosteService } from '../../../services/poste/poste-services';
import { AuthService, UtilisateurCourant } from '../../../services/auth/auth.service';
import { ThemeService } from '../../../services/Theme/theme-service';
import { ContratModel } from '../../../models/contrats';

@Component({
  selector: 'app-contrats',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: 'contrats.html',
  styleUrl: 'contrats.css',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class ContratsComponent implements OnInit {
  private contratService = inject(ContratService);
  private employeService = inject(EmployeeService);
  private posteService = inject(PosteService);
  private authService = inject(AuthService);
  private router = inject(Router);
  private cdr = inject(ChangeDetectorRef);
  themeService = inject(ThemeService);

  private posteMap = new Map<number, string>();

  user: UtilisateurCourant = this.authService.getCurrentUser();
  contrats: ContratModel[] = [];
  listeEmployes: any[] = [];
  listePostes: any[] = [];
  chargement = false;
  chargementForm = false;
  successMessage = '';
  errorMessage = '';
  modeAffichage: 'liste' | 'formulaire' = 'liste';
  recherche = '';
  filtreStatut = '';
  contratACloturer: ContratModel | null = null;
  nouveauContrat: Partial<ContratModel> = this.initialiserFormulaire();
  private chargementsEnCours = 2;

  ngOnInit(): void {
    this.user = this.authService.getCurrentUser();
    this.chargerContrats();
    this.chargerDonneesFormulaire();
  }

  get isRH(): boolean {
    return (this.user?.role ?? '').toUpperCase() === 'RH';
  }
  get isAdmin(): boolean {
    return (this.user?.role ?? '').toUpperCase() === 'ADMIN';
  }
  get isManager(): boolean {
    const role = (this.user?.role ?? '').toUpperCase();
    return role === 'RH' || role === 'ADMIN';
  }
  get isEmploye(): boolean {
    return (this.user?.role ?? '').toUpperCase() === 'EMPLOYE';
  }
  get isDarkMode(): boolean {
    return this.themeService.isDarkMode();
  }

  get nbActifs(): number {
    return this.contrats.filter((c) => c.statut === 'ACTIF').length;
  }
  get nbTermines(): number {
    return this.contrats.filter((c) => c.statut === 'TERMINE').length;
  }
  get nbSuspendus(): number {
    return this.contrats.filter((c) => c.statut === 'SUSPENDU').length;
  }

  get contratsFiltres(): ContratModel[] {
    return this.contrats.filter((c) => {
      const terme = this.recherche.toLowerCase().trim();
      const matchTexte =
        !terme ||
        (c.employe_details?.nom || '').toLowerCase().includes(terme) ||
        (c.employe_details?.prenom || '').toLowerCase().includes(terme) ||
        (c.type_contrat || '').toLowerCase().includes(terme) ||
        (this.getNomPoste(c.poste_details, c.poste) || '').toLowerCase().includes(terme);
      const matchStatut = !this.filtreStatut || c.statut === this.filtreStatut;
      return matchTexte && matchStatut;
    });
  }

  chargerContrats(): void {
    this.chargement = true;
    this.cdr.markForCheck();

    this.contratService.getContrats().subscribe({
      next: (data: any) => {
        this.contrats = Array.isArray(data) ? data : data.results || [];
        this.chargement = false;
        this.cdr.markForCheck();
      },
      error: () => {
        this.errorMessage = 'Impossible de récupérer la liste des contrats.';
        this.chargement = false;
        this.cdr.markForCheck();
      },
    });
  }

  chargerDonneesFormulaire(): void {
    this.chargementForm = true;
    this.chargementsEnCours = 2;
    this.cdr.markForCheck();

    this.employeService.getEmployes().subscribe({
      next: (data: any) => {
        this.listeEmployes = Array.isArray(data) ? data : data.results || [];
        this.verifierChargementComplet();
      },
      error: () => {
        this.listeEmployes = [];
        this.verifierChargementComplet();
      },
    });

    this.posteService.getPostes().subscribe({
      next: (data: any) => {
        this.listePostes = Array.isArray(data) ? data : data.results || [];

        this.posteMap.clear();
        this.listePostes.forEach((p) => {
          if (p.id) {
            this.posteMap.set(p.id, p.intitule || p.nom || 'Poste inconnu');
          }
        });

        this.verifierChargementComplet();
      },
      error: () => {
        this.listePostes = [];
        this.verifierChargementComplet();
      },
    });
  }

  private verifierChargementComplet(): void {
    this.chargementsEnCours--;
    if (this.chargementsEnCours === 0) {
      this.chargementForm = false;
      this.cdr.markForCheck();
    }
  }

  allerVersEmployes(): void {
    this.router.navigate(['/employees']);
  }
  allerVersPostes(): void {
    this.router.navigate(['/postes']);
  }

  soumettreContrat(form: NgForm): void {
    if (form.invalid) return;

    this.chargement = true;
    this.cdr.markForCheck();

    const payload: ContratModel = {
      ...(this.nouveauContrat as ContratModel),
      employe: Number(this.nouveauContrat.employe),
      poste: Number(this.nouveauContrat.poste),
    };

    this.contratService.creerContrat(payload).subscribe({
      next: () => {
        this.successMessage = 'Contrat créé avec succès !';
        this.chargerContrats();
        this.retourListe(form);
        this.masquerMessages();
        this.cdr.markForCheck();
      },
      error: (err) => {
        if (err.error && typeof err.error === 'object') {
          this.errorMessage =
            err.error.date_fin ||
            err.error.non_field_errors ||
            err.error.detail ||
            'Données invalides.';
        } else {
          this.errorMessage = 'Une erreur technique est survenue.';
        }
        this.chargement = false;
        this.cdr.markForCheck();
      },
    });
  }

  demanderCloture(contrat: ContratModel): void {
    this.contratACloturer = contrat;
  }

  annulerCloture(): void {
    this.contratACloturer = null;
  }

  confirmerCloture(): void {
    if (!this.contratACloturer?.id) return;

    this.chargement = true;
    this.cdr.markForCheck();

    this.contratService.cloturerContrat(this.contratACloturer.id).subscribe({
      next: () => {
        this.successMessage = 'Contrat clôturé avec succès.';
        this.annulerCloture();
        this.chargerContrats();
        this.masquerMessages();
        this.cdr.markForCheck();
      },
      error: () => {
        this.errorMessage = 'Erreur lors de la clôturation du contrat.';
        this.chargement = false;
        this.cdr.markForCheck();
      },
    });
  }

  imprimerPDF(contrat: ContratModel): void {
    if (!contrat.id) return;
    const nom = contrat.employe_details
      ? `${contrat.employe_details.nom}_${contrat.employe_details.prenom}`
      : 'employe';
    this.contratService.telechargerContratPDF(contrat.id, nom);
  }

  retourListe(form?: NgForm): void {
    this.modeAffichage = 'liste';
    this.errorMessage = '';
    this.successMessage = '';
    if (form) form.resetForm();
    this.nouveauContrat = this.initialiserFormulaire();
    this.cdr.markForCheck();
  }

  toggleTheme(): void {
    this.themeService.toggleTheme();
  }

  dismissModal(): void {
    this.successMessage = '';
    this.errorMessage = '';
    this.cdr.markForCheck();
  }

  trackById(index: number, item: any): number {
    return item.id ?? index;
  }

  getNomPoste(posteDetails: any, posteId?: number): string {
    // Cas 1 : On a l'objet complet (poste_details)
    if (posteDetails && typeof posteDetails === 'object') {
      return posteDetails.intitule || posteDetails.nom || posteDetails.titre || '—';
    }

    // Cas 2 : On n'a que l'ID (poste), on cherche dans notre carte
    if (posteId && this.posteMap.has(posteId)) {
      return this.posteMap.get(posteId)!;
    }

    return '—';
  }


  private initialiserFormulaire(): Partial<ContratModel> {
    return {
      employe: undefined,
      poste: undefined,
      type_contrat: 'CDI',
      statut: 'ACTIF',
      date_debut: '',
      date_fin: null,
      salaire_base: 0,
    };
  }

  private masquerMessages(): void {
    setTimeout(() => {
      this.successMessage = '';
      this.errorMessage = '';
      this.cdr.markForCheck();
    }, 5000);
  }
}
