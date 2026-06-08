import {
  ChangeDetectionStrategy,
  ChangeDetectorRef,
  Component,
  OnInit,
  inject,
} from '@angular/core';
import { CommonModule, DatePipe } from '@angular/common';
import { RouterModule } from '@angular/router';
import { BaseChartDirective } from 'ng2-charts';
import { ChartData, ChartOptions } from 'chart.js';

import { AuthService } from '../../../services/auth/auth.service';
import { PresenceService } from '../../../services/presence/presence';
import { CongeService } from '../../../services/conges/conges';

@Component({
  selector: 'app-dashboard-employe',
  standalone: true,
  imports: [CommonModule, DatePipe, BaseChartDirective, RouterModule],
  templateUrl: './dashboard-employe.html',
  styleUrl: './dashboard-employe.css',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class DashboardEmploye implements OnInit {
  private authService = inject(AuthService);
  private presenceService = inject(PresenceService);
  private congeService = inject(CongeService);
  private cdr = inject(ChangeDetectorRef);

  today = new Date();
  chargement = true;
  errorMessage = '';
  user = this.authService.getCurrentUser();

  afficherTousLesConges = false;

  // Stats personnelles
  mesPresencesMois = 0;
  mesRetardsMois = 0;
  mesAbsencesMois = 0;

  // Congés
  congesJoursPris = 0;
  congesEnAttente = 0;
  congesApprouves = 0;
  congesRefuses = 0;
  congesTotalDemandes = 0;

  readonly CONGE_REF = 30;

  tousLesConges: any[] = [];
  mesConges: any[] = [];

  // ══════════════════════════════════════════════════════════
  // RECHERCHE & FILTRES DU TABLEAU
  // ══════════════════════════════════════════════════════════
  rechercheConge = '';
  filtreStatut: 'TOUS' | 'EN_ATTENTE' | 'APPROUVE' | 'REFUSE' = 'TOUS';
  triColonne: 'date_debut' | 'date_fin' | 'statut' | 'type_conge' = 'date_debut';
  triDirection: 'asc' | 'desc' = 'desc';
  pageActuelle = 1;
  itemsParPage = 5;

  // ══════════════════════════════════════════════════════════
  // GRAPHIQUE
  // ══════════════════════════════════════════════════════════
  public barChartType: 'bar' = 'bar';
  public barChartData: ChartData<'bar'> = {
    labels: ['Sem 1', 'Sem 2', 'Sem 3', 'Sem 4'],
    datasets: [
      {
        data: [0, 0, 0, 0],
        label: 'Présents',
        backgroundColor: 'rgba(29, 158, 117, 0.85)',
        borderColor: '#1D9E75',
        borderWidth: 2,
        borderRadius: 8,
        borderSkipped: false,
      },
      {
        data: [0, 0, 0, 0],
        label: 'Absents',
        backgroundColor: 'rgba(226, 75, 74, 0.85)',
        borderColor: '#E24B4A',
        borderWidth: 2,
        borderRadius: 8,
        borderSkipped: false,
      },
      {
        data: [0, 0, 0, 0],
        label: 'Retards',
        backgroundColor: 'rgba(239, 159, 39, 0.85)',
        borderColor: '#EF9F27',
        borderWidth: 2,
        borderRadius: 8,
        borderSkipped: false,
      },
    ],
  };

  public barChartOptions: ChartOptions<'bar'> = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: { display: false },
      tooltip: {
        backgroundColor: 'rgba(15, 23, 42, 0.95)',
        titleColor: '#fff',
        bodyColor: '#fff',
        padding: 12,
        cornerRadius: 8,
        displayColors: true,
        boxPadding: 6,
      },
    },
    scales: {
      x: {
        grid: { display: false },
        border: { display: false },
        ticks: {
          color: '#64748b',
          font: { size: 12, weight: 'bold' },
        },
      },
      y: {
        beginAtZero: true,
        grid: { color: 'rgba(226, 232, 240, 0.5)' },
        border: { display: false },
        ticks: {
          color: '#64748b',
          font: { size: 11, weight: 'normal' },
          stepSize: 1,
          padding: 8,
        },
      },
    },
    animation: { duration: 1000, easing: 'easeOutQuart' },
  };

  ngOnInit(): void {
    this.chargerStats();
  }

  // ══════════════════════════════════════════════════════════
  // CHARGEMENT DES STATS
  // ══════════════════════════════════════════════════════════
  chargerStats(): void {
    this.chargement = true;
    this.errorMessage = '';
    this.cdr.markForCheck();

    const monthStart = new Date();
    monthStart.setDate(1);

    // Présences
    this.presenceService.getPresences().subscribe({
      next: (presences) => {
        const mesPresences = presences.filter((p: any) => {
          const pDate = new Date(p.date);
          return pDate >= monthStart && pDate <= new Date();
        });

        this.mesPresencesMois = mesPresences.filter((p: any) => p.statut === 'PRESENT').length;
        this.mesAbsencesMois = mesPresences.filter((p: any) => p.statut === 'ABSENT').length;
        this.mesRetardsMois = mesPresences.filter((p: any) => p.statut === 'RETARD').length;

        const semainesPresents = [0, 0, 0, 0];
        const semainesAbsents = [0, 0, 0, 0];
        const semainesRetards = [0, 0, 0, 0];

        mesPresences.forEach((p: any) => {
          const jour = new Date(p.date).getDate();
          const semaine = Math.min(Math.floor((jour - 1) / 7), 3);
          if (p.statut === 'PRESENT') semainesPresents[semaine]++;
          else if (p.statut === 'ABSENT') semainesAbsents[semaine]++;
          else if (p.statut === 'RETARD') semainesRetards[semaine]++;
        });

        this.barChartData = {
          ...this.barChartData,
          datasets: [
            { ...this.barChartData.datasets[0], data: semainesPresents },
            { ...this.barChartData.datasets[1], data: semainesAbsents },
            { ...this.barChartData.datasets[2], data: semainesRetards },
          ],
        };
        this.cdr.markForCheck();
      },
      error: (err) => {
        this.errorMessage = 'Erreur lors du chargement des présences.';
        this.cdr.markForCheck();
        console.error('Erreur présences:', err);
      },
    });

    // Congés
    this.congeService.getConges().subscribe({
      next: (conges) => {
        this.tousLesConges = conges;
        this.mesConges = this.filtrerMesConges(conges);

        this.congesEnAttente = this.mesConges.filter((c) =>
          this.isStatut(c.statut, ['EN_ATTENTE', 'EN ATTENTE', 'PENDING']),
        ).length;
        this.congesApprouves = this.mesConges.filter((c) =>
          this.isStatut(c.statut, ['APPROUVE', 'APPROUVÉ', 'APPROVED']),
        ).length;
        this.congesRefuses = this.mesConges.filter((c) =>
          this.isStatut(c.statut, ['REFUSE', 'REFUSÉ', 'REJECTED']),
        ).length;

        this.congesJoursPris = this.mesConges
          .filter((c) => this.isStatut(c.statut, ['APPROUVE', 'APPROUVÉ', 'APPROVED']))
          .reduce((total, c) => total + this.calculerJoursConge(c), 0);

        this.congesTotalDemandes = this.mesConges.length;

        this.chargement = false;
        this.cdr.markForCheck();
      },
      error: (err) => {
        this.chargement = false;
        this.errorMessage = 'Erreur lors du chargement des congés.';
        this.cdr.markForCheck();
        console.error('Erreur congés:', err);
      },
    });
  }

  // ══════════════════════════════════════════════════════════
  // FILTRAGE PAR NOM
  // ══════════════════════════════════════════════════════════
  private filtrerMesConges(conges: any[]): any[] {
    if (!this.user) return [];

    const userId = this.user.id;
    const prenom = (this.user.prenom || '').trim().toLowerCase();
    const nom = (this.user.nom || '').trim().toLowerCase();

    return conges.filter((c: any) => {
      if (c.employe === userId || c.employe_id === userId) return true;
      if (c.employe?.id === userId) return true;
      if (String(c.employe) === String(userId)) return true;

      const employeNom = (c.employe_nom || '').toLowerCase().trim();
      if (!employeNom) return false;

      const matchPrenom = prenom && employeNom.includes(prenom);
      const matchNom = nom && employeNom.includes(nom);

      if (prenom && nom && matchPrenom && matchNom) return true;

      if ((matchPrenom || matchNom) && prenom && nom) {
        const autresMatches = conges.filter((other) => {
          const otherNom = (other.employe_nom || '').toLowerCase();
          return otherNom !== employeNom && (otherNom.includes(prenom) || otherNom.includes(nom));
        });
        if (autresMatches.length === 0) return true;
      }

      return false;
    });
  }

  // ══════════════════════════════════════════════════════════
  // HELPERS STATUT
  // ══════════════════════════════════════════════════════════
  isStatut(statut: string, valeurs: string[]): boolean {
    if (!statut) return false;
    const s = statut.toString().toUpperCase().trim().replace(/\s+/g, '_');
    return valeurs.some((v) => s === v.toUpperCase().replace(/\s+/g, '_'));
  }

  private calculerJoursConge(conge: any): number {
    if (!conge.date_debut || !conge.date_fin) return 1;
    const debut = new Date(conge.date_debut);
    const fin = new Date(conge.date_fin);
    if (isNaN(debut.getTime()) || isNaN(fin.getTime())) return 1;

    let jours = 0;
    const current = new Date(debut);
    while (current <= fin) {
      const dayOfWeek = current.getDay();
      if (dayOfWeek !== 0 && dayOfWeek !== 6) jours++;
      current.setDate(current.getDate() + 1);
    }
    return Math.max(1, jours);
  }

  // ══════════════════════════════════════════════════════════
  // ACTIONS DU TABLEAU
  // ══════════════════════════════════════════════════════════
  toggleTousLesConges(): void {
    this.afficherTousLesConges = !this.afficherTousLesConges;
    this.pageActuelle = 1;
    this.cdr.markForCheck();
  }

  filtrerParStatut(statut: 'TOUS' | 'EN_ATTENTE' | 'APPROUVE' | 'REFUSE'): void {
    this.filtreStatut = statut;
    this.pageActuelle = 1;
    this.cdr.markForCheck();
  }

  rechercherConge(event: Event): void {
    const input = event.target as HTMLInputElement;
    this.rechercheConge = input.value;
    this.pageActuelle = 1;
    this.cdr.markForCheck();
  }

  reinitialiserFiltres(): void {
    this.rechercheConge = '';
    this.filtreStatut = 'TOUS';
    this.triColonne = 'date_debut';
    this.triDirection = 'desc';
    this.pageActuelle = 1;
    this.cdr.markForCheck();
  }

  trierPar(colonne: 'date_debut' | 'date_fin' | 'statut' | 'type_conge'): void {
    if (this.triColonne === colonne) {
      this.triDirection = this.triDirection === 'asc' ? 'desc' : 'asc';
    } else {
      this.triColonne = colonne;
      this.triDirection = 'desc';
    }
    this.cdr.markForCheck();
  }

  getTriIcon(colonne: string): string {
    if (this.triColonne !== colonne) return 'bi-arrow-down-up';
    return this.triDirection === 'asc' ? 'bi-caret-up-fill' : 'bi-caret-down-fill';
  }

  changerPage(page: number): void {
    if (page >= 1 && page <= this.totalPages) {
      this.pageActuelle = page;
      this.cdr.markForCheck();
    }
  }

  // ══════════════════════════════════════════════════════════
  // GETTERS
  // ══════════════════════════════════════════════════════════
  get congesAffiches(): any[] {
    return this.afficherTousLesConges ? this.tousLesConges : this.mesConges;
  }

  get congesFiltres(): any[] {
    let resultats = [...this.congesAffiches];

    if (this.filtreStatut !== 'TOUS') {
      resultats = resultats.filter((c) => this.isStatut(c.statut, [this.filtreStatut]));
    }

    if (this.rechercheConge.trim()) {
      const terme = this.rechercheConge.toLowerCase().trim();
      resultats = resultats.filter((c) => {
        const nom = this.getNomEmploye(c).toLowerCase();
        const type = (c.type_label || c.type_conge || '').toLowerCase();
        const motif = (c.motif || '').toLowerCase();
        return nom.includes(terme) || type.includes(terme) || motif.includes(terme);
      });
    }

    resultats.sort((a, b) => {
      let valA: any, valB: any;
      switch (this.triColonne) {
        case 'date_debut':
          valA = new Date(a.date_debut).getTime() || 0;
          valB = new Date(b.date_debut).getTime() || 0;
          break;
        case 'date_fin':
          valA = new Date(a.date_fin).getTime() || 0;
          valB = new Date(b.date_fin).getTime() || 0;
          break;
        case 'statut':
          valA = this.getStatutLabel(a.statut);
          valB = this.getStatutLabel(b.statut);
          break;
        case 'type_conge':
          valA = (a.type_label || a.type_conge || '').toLowerCase();
          valB = (b.type_label || b.type_conge || '').toLowerCase();
          break;
        default:
          return 0;
      }
      if (valA < valB) return this.triDirection === 'asc' ? -1 : 1;
      if (valA > valB) return this.triDirection === 'asc' ? 1 : -1;
      return 0;
    });

    return resultats;
  }

  get congesPagines(): any[] {
    const debut = (this.pageActuelle - 1) * this.itemsParPage;
    return this.congesFiltres.slice(debut, debut + this.itemsParPage);
  }

  get totalPages(): number {
    return Math.ceil(this.congesFiltres.length / this.itemsParPage) || 1;
  }

  get pages(): number[] {
    return Array.from({ length: this.totalPages }, (_, i) => i + 1);
  }

  get totalCongesTousEmployes(): number {
    return this.tousLesConges.length;
  }

  get congesApprouvesTous(): number {
    return this.tousLesConges.filter((c) =>
      this.isStatut(c.statut, ['APPROUVE', 'APPROUVÉ', 'APPROVED']),
    ).length;
  }

  get congesEnAttenteTous(): number {
    return this.tousLesConges.filter((c) =>
      this.isStatut(c.statut, ['EN_ATTENTE', 'EN ATTENTE', 'PENDING']),
    ).length;
  }

  get congesPourcent(): number {
    return Math.round((this.congesJoursPris / this.CONGE_REF) * 100);
  }

  get tauxPresence(): number {
    const total = this.mesPresencesMois + this.mesAbsencesMois + this.mesRetardsMois;
    if (total === 0) return 0;
    return Math.round((this.mesPresencesMois / total) * 100);
  }

  get nomComplet(): string {
    if (!this.user) return 'Employé';
    const prenom = this.user.prenom || '';
    const nom = this.user.nom || '';
    return `${prenom} ${nom}`.trim() || 'Employé';
  }

  // ══════════════════════════════════════════════════════════
  // HELPERS D'AFFICHAGE
  // ══════════════════════════════════════════════════════════
  getNomEmploye(conge: any): string {
    if (!conge) return 'Employé';
    if (conge.employe_nom && typeof conge.employe_nom === 'string') {
      return conge.employe_nom;
    }
    if (conge.employe && typeof conge.employe === 'object') {
      return `${conge.employe.prenom || ''} ${conge.employe.nom || ''}`.trim() || 'Employé';
    }
    return 'Employé';
  }

  getStatutClass(statut: string): string {
    if (this.isStatut(statut, ['APPROUVE', 'APPROUVÉ', 'APPROVED'])) return 'statut--success';
    if (this.isStatut(statut, ['EN_ATTENTE', 'EN ATTENTE', 'PENDING'])) return 'statut--warning';
    if (this.isStatut(statut, ['REFUSE', 'REFUSÉ', 'REJECTED'])) return 'statut--danger';
    return '';
  }

  getStatutLabel(statut: string): string {
    if (this.isStatut(statut, ['APPROUVE', 'APPROUVÉ', 'APPROVED'])) return 'Approuvé';
    if (this.isStatut(statut, ['EN_ATTENTE', 'EN ATTENTE', 'PENDING'])) return 'En attente';
    if (this.isStatut(statut, ['REFUSE', 'REFUSÉ', 'REJECTED'])) return 'Refusé';
    return statut || 'Inconnu';
  }

  estEnAttente(statut: string): boolean {
    return this.isStatut(statut, ['EN_ATTENTE', 'EN ATTENTE', 'PENDING']);
  }

  estApprouve(statut: string): boolean {
    return this.isStatut(statut, ['APPROUVE', 'APPROUVÉ', 'APPROVED']);
  }

  estRefuse(statut: string): boolean {
    return this.isStatut(statut, ['REFUSE', 'REFUSÉ', 'REJECTED']);
  }

  getDureeLabel(conge: any): string {
    const jours = this.calculerJoursConge(conge);
    if (jours === 0) return '—';
    if (jours === 1) return '1 jour';
    return `${jours} jours`;
  }

  getTypeIcon(type: string): string {
    const t = (type || '').toLowerCase();
    if (t.includes('annuel') || t.includes('vacance')) return 'bi-sun-fill';
    if (t.includes('maladie') || t.includes('medical')) return 'bi-hospital';
    if (t.includes('maternite') || t.includes('paternite')) return 'bi-heart-fill';
    if (t.includes('formation')) return 'bi-mortarboard-fill';
    if (t.includes('familial') || t.includes('famille')) return 'bi-people-fill';
    if (t.includes('exception')) return 'bi-star-fill';
    return 'bi-tag-fill';
  }
}
