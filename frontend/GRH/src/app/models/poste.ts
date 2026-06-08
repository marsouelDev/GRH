export type NiveauHierarchie = 'JUNIOR' | 'INTERMEDIAIRE' | 'SENIOR' | 'MANAGER' | 'DIRECTEUR';

export interface PosteModel {
  id?: number;
  intitule: string;
  description?: string;
  niveau_hierarchie: NiveauHierarchie;
  niveau_label?: string;
  salaire_min: number;
  salaire_max: number;
  est_actif?: boolean;
  date_creation?: string;
  nombre_occupants?: number;
  vacant?: boolean;
  employes?: number[];
}
