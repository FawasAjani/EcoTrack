import { Injectable, signal } from '@angular/core';

export type ThemePreference = 'light' | 'dark' | 'system';

@Injectable({
  providedIn: 'root'
})
export class ThemeService {
  private readonly storageKey = 'ecotrack-theme';

  readonly theme = signal<ThemePreference>(this.getSavedTheme());

  constructor() {
    this.applyTheme(this.theme());

    window.matchMedia('(prefers-color-scheme: dark)')
      .addEventListener('change', () => {
        if (this.theme() === 'system') {
          this.applyTheme('system');
        }
      });
  }

  setTheme(theme: ThemePreference): void {
    this.theme.set(theme);
    localStorage.setItem(this.storageKey, theme);
    this.applyTheme(theme);
  }

  private getSavedTheme(): ThemePreference {
    const savedTheme = localStorage.getItem(this.storageKey);

    if (
      savedTheme === 'light' ||
      savedTheme === 'dark' ||
      savedTheme === 'system'
    ) {
      return savedTheme;
    }

    return 'system';
  }

  private applyTheme(theme: ThemePreference): void {
    const isDark = theme === 'dark' ||
      (theme === 'system' &&
        window.matchMedia('(prefers-color-scheme: dark)').matches);

    document.documentElement.setAttribute(
      'data-theme',
      isDark ? 'dark' : 'light'
    );
  }
}