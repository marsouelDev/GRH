export interface EmployeModels {
  id?: number;
  email: string;
  nom: string;
  prenom: string;
  date_naissance: string;
  telephone: string;
  salaire: number;
  is_active?: boolean;
  date_joined?: string;
  notification?: string; // Capturera le message d'envoi du mail de Django
}
