export interface AdministrateursModels {
  id?: number;
  email: string;
  nom: string;
  prenom: string;
  date_naissance: string;
  telephone: string;
  is_active?: boolean;
  date_joined?: string;
  notification?: string;
}
