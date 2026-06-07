import { Injectable, signal, effect } from '@angular/core';

@Injectable({ providedIn: 'root' })
export class ThemeService {
  isDarkMode = signal<boolean>(false);

  constructor() {
    //  Effet automatique (sans allowSignalWrites - déprécié en Angular 19+)
    effect(() => {
      const dark = this.isDarkMode();

      // Appliquer sur body ET html pour une compatibilité maximale
      document.body.classList.toggle('dark', dark);
      document.documentElement.classList.toggle('dark', dark);

      // Sauvegarde dans localStorage
      localStorage.setItem('theme', dark ? 'dark' : 'light');
    });

    // Charge le thème sauvegardé au démarrage
    this.loadSavedTheme();
  }

  toggleTheme(): void {
    this.isDarkMode.update((mode) => !mode);
  }

  setDarkMode(value: boolean): void {
    this.isDarkMode.set(value);
  }

  private loadSavedTheme(): void {
    const saved = localStorage.getItem('theme');
    if (saved === 'dark') {
      this.isDarkMode.set(true);
    }
  }
}
