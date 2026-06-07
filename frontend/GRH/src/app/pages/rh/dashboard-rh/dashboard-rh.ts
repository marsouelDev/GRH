import { NgIf } from '@angular/common';
import { Component } from '@angular/core';

@Component({
  selector: 'app-dashboard-rh',
  imports: [NgIf],
  templateUrl: './dashboard-rh.html',
  styleUrl: './dashboard-rh.css',
})
export class DashboardRh {
  stats = {
    employes: 85,
    congesEnAttente: 6,
    contrats: 70,
    presences: 40,
  };
}
