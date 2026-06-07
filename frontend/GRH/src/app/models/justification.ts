export type StatutJustif = 'EN_ATTENTE' | 'VALIDEE' | 'REFUSEE';
export type TypeJustif = 'RETARD' | 'ABSENCE';

export interface Justification {
  id: number;
  presence?: number;
  presence_date?: string;
  employe?: number;
  employe_nom?: string;
  type_justif: TypeJustif;
  type_label?: string;
  motif: string;
  document?: string | null;
  document_url?: string | null;
  statut: StatutJustif;
  statut_label?: string;
  date_soumission?: string;
  commentaire?: string | null;
  valide_par?: number;
  valide_par_nom?: string;
  date_validation?: string;
}

export interface NouvelleJustif {
  presence: number | null;
  type_justif: TypeJustif | null;
  motif: string;
}
