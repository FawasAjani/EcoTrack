
import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import {
  FormControl,
  ReactiveFormsModule,
  Validators
} from '@angular/forms';
import { Router } from '@angular/router';
import { SupabaseService } from '../supabase.service';

@Component({
  selector: 'app-reset-password',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule],
  templateUrl: './reset-password.html',
  styleUrl: './reset-password.css'
})
export class ResetPassword {
  password = new FormControl('', [
    Validators.required,
    Validators.minLength(8)
  ]);

  confirmPassword = new FormControl('', [
    Validators.required
  ]);

  message = '';
  messageType: 'success' | 'error' = 'error';
  isLoading = false;

  constructor(
    private supabaseService: SupabaseService,
    private router: Router
  ) {}

  async onSubmit(): Promise<void> {
    this.message = '';

    this.password.markAsTouched();
    this.confirmPassword.markAsTouched();

    if (this.password.invalid || this.confirmPassword.invalid) {
      this.message = 'Please enter a password of at least 8 characters and confirm it.';
      this.messageType = 'error';
      return;
    }

    if (this.password.value !== this.confirmPassword.value) {
      this.message = 'Your passwords do not match.';
      this.messageType = 'error';
      return;
    }

    this.isLoading = true;

    try {
      const { error } = await this.supabaseService.updatePassword(
        this.password.value ?? ''
      );

      if (error) {
        this.message = error.message;
        this.messageType = 'error';
        return;
      }

      this.message = 'Your password has been updated successfully.';
      this.messageType = 'success';

      await this.router.navigate(['/login']);

    } catch (error) {
      console.error('Password update error:', error);
      this.message = 'Unable to update your password. Please try again.';
      this.messageType = 'error';

    } finally {
      this.isLoading = false;
    }
  }

  goToLogin(): void {
    this.router.navigate(['/login']);
  }
}
