export type TypeContrat = 'CDI' | 'CDD' | 'STAGE' | 'FREELANCE';
export type StatutContrat = 'ACTIF' | 'TERMINE' | 'SUSPENDU';

export interface ContratModel {
  poste_details: any;
  id?: number;
  employe: number;
  employe_details?: any; 
  poste: number;
  poste_intitule?: string; 
  type_contrat: TypeContrat;
  date_debut: string;  
  date_fin?: string | null;
  salaire_base: number;
  statut?: StatutContrat;
}
