import {
  ChangeDetectionStrategy,
  ChangeDetectorRef,
  Component,
  OnInit,
  inject,
} from '@angular/core';
import { RouterModule } from '@angular/router';
import { CommonModule, DatePipe } from '@angular/common';
import { BaseChartDirective } from 'ng2-charts';
import { ChartData, ChartOptions } from 'chart.js';

import { AuthService } from '../../../services/auth/auth.service';
import { Dashboard } from '../../../services/dashboard/dashboard';
import { ThemeService } from '../../../services/Theme/theme-service';
import { DashboardStats } from '../../../models/analytics';

@Component({
  selector: 'app-dashboard-admin',
  standalone: true,
  imports: [CommonModule, RouterModule, DatePipe, BaseChartDirective],
  templateUrl: './dashboard-admin.html',
  styleUrls: ['./dashboard-admin.css'],
  // ✅ OPTIMISATION : OnPush pour de meilleures performances
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class DashboardAdmin implements OnInit {
  private authService = inject(AuthService);
  private analyticsService = inject(Dashboard);
  private themeService = inject(ThemeService);

  // ✅ ChangeDetectorRef pour contrôler la détection de changements
  private cdr = inject(ChangeDetectorRef);

  today = new Date();
  chargement = true;
  errorMessage = '';
  stats!: DashboardStats;

  get isDarkMode(): boolean {
    return this.themeService.isDarkMode();
  }

  // ── Couleurs partagées ──────────────────────────────────
  private readonly C_GREEN = '#1D9E75';
  private readonly C_RED = '#E24B4A';
  private readonly C_AMBER = '#EF9F27';

  private get tooltipStyle(): object {
    const dark = this.isDarkMode;
    return {
      backgroundColor: dark ? '#161b22' : '#ffffff',
      borderColor: dark ? '#30363d' : '#e2e8f0',
      borderWidth: 1,
      titleColor: dark ? '#e6edf3' : '#0f172a',
      bodyColor: dark ? '#8b949e' : '#475569',
      padding: 12,
      cornerRadius: 10,
      boxPadding: 5,
    };
  }

  private get gridColor(): string {
    return this.isDarkMode ? 'rgba(255,255,255,.06)' : 'rgba(0,0,0,.05)';
  }

  private get baseScales() {
    const tick = this.isDarkMode ? '#8b949e' : '#94a3b8';
    return {
      x: {
        grid: { display: false },
        border: { display: false },
        ticks: { color: tick, font: { size: 11 } },
      },
      y: {
        beginAtZero: true,
        border: { display: false },
        grid: { color: this.gridColor },
        ticks: { color: tick, font: { size: 11 }, stepSize: 1 },
      },
    };
  }

  // ── Barres — présences semaine ─────────────────────────
  barChartType: 'bar' = 'bar';

  barChartData: ChartData<'bar'> = {
    labels: [],
    datasets: [
      {
        data: [],
        label: 'Présents',
        backgroundColor: '#1D9E75',
        borderRadius: { topLeft: 4, topRight: 4 } as any,
        borderSkipped: false,
      },
      {
        data: [],
        label: 'Absents',
        backgroundColor: '#E24B4A',
        borderRadius: { topLeft: 4, topRight: 4 } as any,
        borderSkipped: false,
      },
      {
        data: [],
        label: 'Retards',
        backgroundColor: '#EF9F27',
        borderRadius: { topLeft: 4, topRight: 4 } as any,
        borderSkipped: false,
      },
    ],
  };

  barChartOptions: ChartOptions<'bar'> = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: { display: false },
      tooltip: { ...this.tooltipStyle } as any,
    },
    scales: this.baseScales as any,
  };

  // ── Ligne — évolution 12 mois ──────────────────────────
  lineChartType: 'line' = 'line';

  lineChartData: ChartData<'line'> = {
    labels: [],
    datasets: [
      {
        data: [],
        label: 'Présents',
        borderColor: '#1D9E75',
        backgroundColor: 'rgba(29,158,117,.10)',
        borderWidth: 2,
        fill: true,
        tension: 0.4,
        pointRadius: 3,
        pointHoverRadius: 6,
        pointBackgroundColor: '#1D9E75',
        pointBorderColor: '#ffffff',
        pointBorderWidth: 2,
      },
      {
        data: [],
        label: 'Absents',
        borderColor: '#E24B4A',
        backgroundColor: 'rgba(226,75,74,.08)',
        borderWidth: 2,
        fill: true,
        tension: 0.4,
        borderDash: [5, 3],
        pointRadius: 3,
        pointHoverRadius: 6,
        pointBackgroundColor: '#E24B4A',
        pointBorderColor: '#ffffff',
        pointBorderWidth: 2,
      },
      {
        data: [],
        label: 'Retards',
        borderColor: '#EF9F27',
        backgroundColor: 'rgba(239,159,39,.08)',
        borderWidth: 2,
        fill: true,
        tension: 0.4,
        pointRadius: 3,
        pointHoverRadius: 6,
        pointBackgroundColor: '#EF9F27',
        pointBorderColor: '#ffffff',
        pointBorderWidth: 2,
      },
    ],
  };

  lineChartOptions: ChartOptions<'line'> = {
    responsive: true,
    maintainAspectRatio: false,
    interaction: { mode: 'index', intersect: false },
    plugins: {
      legend: { display: false },
      tooltip: { ...this.tooltipStyle } as any,
    },
    scales: this.baseScales as any,
  };

  // ── Donut — répartition du jour ────────────────────────
  doughnutChartType: 'doughnut' = 'doughnut';

  doughnutChartData: ChartData<'doughnut'> = {
    labels: [],
    datasets: [
      {
        data: [],
        backgroundColor: ['#1D9E75', '#E24B4A', '#EF9F27'],
        borderWidth: 3,
        borderColor: '#ffffff',
        hoverOffset: 6,
      },
    ],
  };

  doughnutChartOptions: ChartOptions<'doughnut'> = {
    responsive: true,
    maintainAspectRatio: false,
    cutout: '68%',
    plugins: {
      legend: { display: false },
      tooltip: {
        ...this.tooltipStyle,
        callbacks: {
          label: (ctx: { dataset: { data: number[] }; parsed: number; label: any }) => {
            const total = (ctx.dataset.data as number[]).reduce((a, b) => a + (b as number), 0);
            const pct = total > 0 ? Math.round((ctx.parsed / total) * 100) : 0;
            return ` ${ctx.label}: ${ctx.parsed} (${pct}%)`;
          },
        },
      } as any,
    },
  };

  // ── Lifecycle ──────────────────────────────────────────
  ngOnInit(): void {
    this.chargerDashboard();
  }

  chargerDashboard(): void {
    this.chargement = true;
    this.errorMessage = '';
    this.cdr.markForCheck(); // ✅ Notifier Angular du début du chargement

    this.analyticsService.getDashboardStats().subscribe({
      next: (data) => {
        this.stats = data;
        this.mettreAJourGraphiques(data);
        this.chargement = false;
        this.cdr.markForCheck(); // ✅ Notifier Angular des nouvelles données
      },
      error: (err) => {
        this.chargement = false;
        this.errorMessage = err?.error?.detail || 'Erreur lors du chargement du dashboard.';
        this.cdr.markForCheck(); // ✅ Notifier Angular de l'erreur
      },
    });
  }

  mettreAJourGraphiques(data: DashboardStats): void {
    const borderColor = this.isDarkMode ? '#161b22' : '#ffffff';

    // Barres
    this.barChartData = {
      ...this.barChartData,
      labels: data.presences_semaine.map((p) => p.jour),
      datasets: [
        { ...this.barChartData.datasets[0], data: data.presences_semaine.map((p) => p.presents) },
        { ...this.barChartData.datasets[1], data: data.presences_semaine.map((p) => p.absents) },
        { ...this.barChartData.datasets[2], data: data.presences_semaine.map((p) => p.retards) },
      ],
    };

    // Ligne
    this.lineChartData = {
      ...this.lineChartData,
      labels: data.evolution_mensuelle.map((m) => m.mois),
      datasets: [
        {
          ...this.lineChartData.datasets[0],
          data: data.evolution_mensuelle.map((m) => m.presents),
          pointBorderColor: borderColor,
        },
        {
          ...this.lineChartData.datasets[1],
          data: data.evolution_mensuelle.map((m) => m.absents),
          pointBorderColor: borderColor,
        },
        {
          ...this.lineChartData.datasets[2],
          data: data.evolution_mensuelle.map((m) => m.retards),
          pointBorderColor: borderColor,
        },
      ],
    };

    // Donut
    this.doughnutChartData = {
      ...this.doughnutChartData,
      labels: data.repartition_statut.map((r) => r.label),
      datasets: [
        {
          ...this.doughnutChartData.datasets[0],
          data: data.repartition_statut.map((r) => r.value),
          borderColor: borderColor,
        },
      ],
    };
  }

  // ── Total pour le centre du donut ─────────────────────
  get totalDuJour(): number {
    if (!this.stats?.repartition_statut) return 0;
    return this.stats.repartition_statut.reduce((s, r) => s + r.value, 0);
  }
}
