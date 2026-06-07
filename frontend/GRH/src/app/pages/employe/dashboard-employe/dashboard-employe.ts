import { Component } from '@angular/core';

@Component({
  selector: 'app-dashboard-employe',
  imports: [],
  templateUrl: './dashboard-employe.html',
  styleUrl: './dashboard-employe.css',
})
export class DashboardEmploye {
  stats = {
    employes: 85,
    congesEnAttente: 6,
    contrats: 70,
    presences: 40,
  };
}
