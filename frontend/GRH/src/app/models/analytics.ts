export interface DashboardStats {
  kpis: {
    total_employes: number;
    nouveaux_ce_mois: number;
    presents_aujourdhui: number;
    absents_aujourdhui: number;
    retards_aujourdhui: number;
    taux_presence: number;
    semaine_presents: number;
    semaine_absents: number;
    semaine_retards: number;
    taux_semaine: number;
    mois_presents: number;
    mois_absents: number;
    mois_retards: number;
    taux_mois: number;
    annee_presents: number;
    annee_absents: number;
    annee_retards: number;
    taux_annee: number;
    conges_en_attente: number;
    conges_approuves: number;
    justifs_en_attente: number;
    justifs_validees: number;
    justifs_rejetees: number;
    alertes: number;
  };
  presences_semaine: Array<{
    jour: string;
    date: string;
    presents: number;
    absents: number;
    retards: number;
  }>;
  evolution_mensuelle: Array<{
    mois: string;
    presents: number;
    absents: number;
    retards: number;
  }>;
  repartition_statut: Array<{
    label: string;
    value: number;
    statut: string;
  }>;
  conges_par_type: Array<{
    type_conge: string;
    total: number;
  }>;
  activites_recentes: Array<{
    type: string;
    icon: string;
    text: string;
    time: string;
  }>;
}

export interface EmployesStats {
  total: number;
  actifs: number;
  inactifs: number;
  par_departement: Array<{ departement: string; total: number }>;
  par_role: Array<{ role: string; total: number }>;
  top_absents_mois: Array<{
    employe__nom: string;
    employe__prenom: string;
    total_absences: number;
  }>;
}
