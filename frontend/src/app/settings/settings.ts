
import { Component, OnInit, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router, RouterLink } from '@angular/router';
import { SupabaseService } from '../supabase.service';
import { ThemeService, ThemePreference } from '../services/theme.service';

@Component({
  selector: 'app-settings',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterLink],
  templateUrl: './settings.html',
  styleUrl: './settings.css',
})
export class Settings implements OnInit {
  fullName = '';
  email = '';

  themePreference: ThemePreference;

  loading = true;
  saving = false;
  loggingOut = false;

  successMessage = '';
  errorMessage = '';

  constructor(
    private supabaseService: SupabaseService,
    private themeService: ThemeService,
    private router: Router,
    private cdr: ChangeDetectorRef
  ) {
    this.themePreference = this.themeService.theme();
  }

  async ngOnInit(): Promise<void> {
    await this.loadProfile();
  }

  async loadProfile(): Promise<void> {
    this.loading = true;
    this.errorMessage = '';
    this.cdr.markForCheck();

    try {
      const { user, error } =
        await this.supabaseService.getUserProfile();

      if (error) {
        throw error;
      }

      if (!user) {
        this.errorMessage =
          'Unable to retrieve your account details. Please sign in again.';
        return;
      }

      this.fullName = user.fullName;
      this.email = user.email;

    } catch (error: any) {
      this.errorMessage =
        error?.message || 'Unable to load your account details.';

    } finally {
      this.loading = false;
      this.cdr.markForCheck();
    }
  }

  onThemeChange(theme: ThemePreference): void {
    this.themePreference = theme;
    this.themeService.setTheme(theme);
  }

  async saveProfile(): Promise<void> {
    this.successMessage = '';
    this.errorMessage = '';

    const trimmedName = this.fullName.trim();

    if (!trimmedName) {
      this.errorMessage = 'Please enter your name.';
      this.cdr.markForCheck();
      return;
    }

    if (trimmedName.length > 100) {
      this.errorMessage =
        'Your name cannot exceed 100 characters.';
      this.cdr.markForCheck();
      return;
    }

    this.saving = true;
    this.cdr.markForCheck();

    try {
      const { error } =
        await this.supabaseService.updateProfile(trimmedName);

      if (error) {
        throw error;
      }

      this.fullName = trimmedName;
      this.successMessage =
        'Your profile has been updated successfully.';

    } catch (error: any) {
      this.errorMessage =
        error?.message || 'Unable to update your profile.';

    } finally {
      this.saving = false;
      this.cdr.markForCheck();
    }
  }

  async logout(): Promise<void> {
    const confirmed = window.confirm(
      'Are you sure you want to log out of EcoTrack?'
    );

    if (!confirmed) {
      return;
    }

    this.loggingOut = true;
    this.errorMessage = '';
    this.successMessage = '';
    this.cdr.markForCheck();

    try {
      const { error } = await this.supabaseService.signOut();

      if (error) {
        throw error;
      }

      await this.router.navigate(['/login']);

    } catch (error: any) {
      this.errorMessage =
        error?.message || 'Unable to log out. Please try again.';

      this.loggingOut = false;
      this.cdr.markForCheck();
    }
  }
}
