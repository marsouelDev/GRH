
export interface Presence {
  id:                number | null;
  employe:           number;
  employe_nom?:      string;
  date:              string;                       
  heure_arrivee:     string | null;
  heure_depart:      string | null;
  statut:            'PRESENT' | 'ABSENT' | 'RETARD';
  statut_label:      string;
  heures_travaillees?: number;
  justifie?:         boolean;                        
}