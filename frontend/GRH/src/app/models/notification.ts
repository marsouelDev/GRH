
export type TypeNotification =
  | 'CONGE_SOUMIS'
  | 'CONGE_APPROUVE'
  | 'CONGE_REFUSE'
  | 'JUSTIF_SOUMISE'
  | 'JUSTIF_VALIDEE'
  | 'JUSTIF_REJETEE'
  | 'ANNIVERSAIRE'
  | 'RAPPEL'
  | 'SYSTEME';

export interface Notification {
  id: number;
  type_notif: TypeNotification;
  type_label: string;
  titre: string;
  message: string;
  lien: string;
  lu: boolean;
  date_envoi: string; 
}
