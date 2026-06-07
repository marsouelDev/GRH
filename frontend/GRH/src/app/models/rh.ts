// src/app/models/rh.ts
export interface RHModel {
  id?: number;
  email: string;
  password?: string;
  nom: string;
  prenom: string;
  date_naissance?: string | null;
  telephone?: string;
  role?: string;
  is_active?: boolean;
  date_joined?: string;
  notification?: string;
}
