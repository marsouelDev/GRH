import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';

@Component({
  selector: 'app-dashboard-admin',
  standalone: true,
  imports: [CommonModule, RouterModule],
  templateUrl: './dashboard-admin.html',
  styleUrls: ['./dashboard-admin.css'],
})
export class DashboardAdmin implements OnInit {
  stats = {
    employes: 0,
    rh: 0,
    contrats: 0,
    conges: 0,
  };

  constructor() {}

  ngOnInit(): void {
    this.loadStats();
  }

  private loadStats(): void {
    // TODO: Appeler votre service pour charger les vraies données
    // Exemple:
    // this.statsService.getAdminStats().subscribe(stats => this.stats = stats);

    // Données factices pour le développement
    this.stats = {
      employes: 42,
      rh: 5,
      contrats: 38,
      conges: 3,
    };
  }
}
