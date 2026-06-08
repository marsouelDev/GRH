import { Component, OnInit, OnDestroy, inject, ChangeDetectionStrategy, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router, NavigationEnd } from '@angular/router';
import { Subscription, filter } from 'rxjs';

import { PresenceService } from '../../services/presence/presence';
import { AuthService, UtilisateurCourant } from '../../services/auth/auth.service';
import { ThemeService } from '../../services/Theme/theme-service';
import { Presence } from '../../models/presences';

@Component({
  selector: 'app-presence-list',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './presence.html',
  styleUrl: './presence.css',
  changeDetection: ChangeDetectionStrategy.OnPush
})
export class PresenceListComponent implements OnInit, OnDestroy {
  // ── Injections ────────────────────────────────────────────
  private presenceService = inject(PresenceService);
  private authService = inject(AuthService);
  private router = inject(Router);
  themeService = inject(ThemeService);
  private cdr = inject(ChangeDetectorRef);

  // ── État ──────────────────────────────────────────────────
  presences: Presence[] = [];
  message = '';
  errorMessage = '';
  chargement = false;

  employeIdFilter?: number;
  recherche = '';
  filtreStatut: 'PRESENT' | 'ABSENT' | 'RETARD' | null = null;

  user!: UtilisateurCourant;
  private routerSub!: Subscription;
  private _timer?: ReturnType<typeof setTimeout>;

  // ── Cycle de vie ──────────────────────────────────────────
  ngOnInit(): void {
    this.user = this.authService.getCurrentUser();
    this.loadPresences();

    this.routerSub = this.router.events
      .pipe(filter((e) => e instanceof NavigationEnd))
      .subscribe(() => {
        this.user = this.authService.getCurrentUser();
        this.loadPresences();
      });
  }

  ngOnDestroy(): void {
    this.routerSub?.unsubscribe();
    clearTimeout(this._timer);
  }

  get isManager(): boolean {
    return ['ADMIN', 'RH'].includes((this.user?.role ?? '').toUpperCase());
  }

  get isEmploye(): boolean {
    return (this.user?.role ?? '').toUpperCase() === 'EMPLOYE';
  }

  get isDarkMode(): boolean {
    return this.themeService.isDarkMode();
  }

  get nomAffiche(): string {
    return this.user?.prenom || this.user?.nom || this.user?.email || 'Employé';
  }

  get presenceAujourdhui(): Presence | null {
    const today = new Date().toISOString().split('T')[0];
    return this.presences.find((p) => {
      const pDate = p.date?.split('T')[0] || p.date;
      return pDate === today;
    }) || null;
  }

  get presencesFiltrees(): Presence[] {
    return this.presences.filter((p) => {
      const terme = this.recherche.toLowerCase().trim();
      const employeNom = p.employe_nom?.toLowerCase() || '';
      const dateStr = p.date?.toLowerCase() || '';
      const matchTexte = !terme || employeNom.includes(terme) || dateStr.includes(terme);
      const matchStatut = !this.filtreStatut || p.statut === this.filtreStatut;
      return matchTexte && matchStatut;
    });
  }

  get nbPresents(): number {
    return this.presences.filter((p) => p.statut === 'PRESENT').length;
  }

  get nbAbsents(): number {
    return this.presences.filter((p) => p.statut === 'ABSENT').length;
  }

  get nbRetards(): number {
    return this.presences.filter((p) => p.statut === 'RETARD').length;
  }

  loadPresences(): void {
    this.errorMessage = '';
    this.chargement = true;
    const filtreId = this.isManager ? this.employeIdFilter : undefined;

    this.presenceService.getPresences(filtreId).subscribe({
      next: (data) => {
        console.log('Presences reçues:', data.length, 'éléments');
        this.presences = data;
        this.chargement = false;
        this.cdr.markForCheck();
      },
      error: (err) => {
        console.error('Erreur presences:', err);
        this.chargement = false;
        this.afficherErreur(err?.error?.detail || 'Erreur lors du chargement.');
        this.cdr.markForCheck();
      },
    });
  }

  badgerArrivee(): void {
    if (!this.isEmploye) return;
    this.reinitialiserMessages();
    this.chargement = true;

    this.presenceService.badgerArrivee().subscribe({
      next: () => {
        this.afficherSucces('Arrivée enregistrée.');
        this.loadPresences();
      },
      error: (err) => {
        this.chargement = false;
        this.afficherErreur(err?.error?.detail || "Impossible de badger l'arrivée.");
        this.cdr.markForCheck();
      },
    });
  }

  badgerDepart(): void {
    if (!this.isEmploye) return;
    this.reinitialiserMessages();
    this.chargement = true;

    this.presenceService.badgerDepart().subscribe({
      next: () => {
        this.afficherSucces('Départ enregistré.');
        this.loadPresences();
      },
      error: (err) => {
        this.chargement = false;
        this.afficherErreur(err?.error?.detail || 'Impossible de badger le départ.');
        this.cdr.markForCheck();
      },
    });
  }

  ouvrirFormulaireJustification(presenceId: number): void {
    this.router.navigate(['/justifications'], { queryParams: { presenceId } });
  }

  getValidPresenceId(p: Presence): number | null {
    return p.id && p.id > 0 ? p.id : null;
  }

  ouvrirFormulaireJustificationSafe(p: Presence): void {
    const id = this.getValidPresenceId(p);
    if (id) {
      this.ouvrirFormulaireJustification(id);
    } else {
      console.warn('⚠️ Impossible de justifier : présence sans ID valide', {
        date: p.date,
        statut: p.statut,
        id: p.id,
      });
    }
  }

  private reinitialiserMessages(): void {
    this.message = '';
    this.errorMessage = '';
    this.cdr.markForCheck();
  }

  private afficherSucces(msg: string): void {
    clearTimeout(this._timer);
    this.message = msg;
    this.errorMessage = '';
    this.cdr.markForCheck();

    this._timer = setTimeout(() => {
      this.message = '';
      this.cdr.markForCheck();
    }, 4000);
  }

  private afficherErreur(msg: string): void {
    clearTimeout(this._timer);
    this.errorMessage = msg;
    this.message = '';
    this.cdr.markForCheck();

    this._timer = setTimeout(() => {
      this.errorMessage = '';
      this.cdr.markForCheck();
    }, 4000);
  }

  dismissModal(): void {
    this.reinitialiserMessages();
  }

  getInitials(p: Presence): string {
    const name = p.employe_nom || 'E';
    const parts = name.trim().split(' ').filter(Boolean);
    if (parts.length >= 2) return (parts[0][0] + parts[1][0]).toUpperCase();
    return parts[0]?.[0]?.toUpperCase() || 'E';
  }

  getAvatarColor(p: Presence): string {
    const colors = ['#2563eb', '#0891b2', '#7c3aed', '#059669', '#d97706', '#dc2626'];
    const name = p.employe_nom || 'default';
    const hash = name.split('').reduce((a, c) => a + c.charCodeAt(0), 0);
    return colors[hash % colors.length];
  }
}