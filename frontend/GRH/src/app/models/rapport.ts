export type TypeRapport =
  | 'EFFECTIFS'
  | 'PRESENCES'
  | 'ABSENCES'
  | 'CONGES'
  | 'JUSTIFICATIONS'
  | 'SALAIRES'
  | 'MENSUEL';

export interface RapportModel {
  id?: number;
  titre: string;
  type_rapport: TypeRapport;
  type_label?: string;
  description?: string;
  genere_par?: number;
  genere_par_nom?: string;
  date_debut?: string | null;
  date_fin?: string | null;
  date_creation?: string;
  donnees?: Record<string, any>;
}
