export type TypeConge = 'ANNUEL' | 'MALADIE' | 'MATERNITE' | 'SANS_SOLDE' | 'AUTRE';
export type StatutConge = 'EN_ATTENTE' | 'APPROUVE' | 'REFUSE' | 'ANNULE';

export interface CongeModel {
commentaire_refus: any;
date_soumission: string|number|Date;
  id?: number;
  employe?: number;
  employe_nom?: string;
  type_conge: TypeConge;
  type_label?: string;
  date_debut: string;
  date_fin: string;
  motif?: string;
  statut: StatutConge;
  statut_label?: string;
  duree_jours?: number;
  date_demande?: string;
  commentaire?: string | null;
  valide_par_nom?: string | null; 
  date_validation?: string | null; 
}
