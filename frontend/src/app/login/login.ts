
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
  selector: 'app-login',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule],
  templateUrl: './login.html',
  styleUrl: './login.css'
})
export class Login {
  email = new FormControl('', [
    Validators.required,
    Validators.email
  ]);

  password = new FormControl('', [
    Validators.required
  ]);

  message = '';
  messageType: 'success' | 'error' = 'error';
  isLoading = false;

  constructor(
    private router: Router,
    private supabaseService: SupabaseService
  ) {}

  async onSubmit(): Promise<void> {
    this.message = '';

    if (this.email.invalid || this.password.invalid) {
      this.email.markAsTouched();
      this.password.markAsTouched();

      this.message = 'Please enter a valid email address and password.';
      this.messageType = 'error';
      return;
    }

    this.isLoading = true;

    try {
      const { data, error } = await this.supabaseService.signIn(
        this.email.value ?? '',
        this.password.value ?? ''
      );

      if (error) {
        this.message = `Login failed: ${error.message}`;
        this.messageType = 'error';
        return;
      }

      if (data.user) {
        this.message = 'Login successful! Welcome to EcoTrack.';
        this.messageType = 'success';

        // Navigate to the dashboard after successful authentication.
        await this.router.navigate(['/home']);
      } else {
        this.message = 'Login could not be completed. Please try again.';
        this.messageType = 'error';
      }

    } catch (error) {
      console.error('Login error:', error);
      this.message = 'Unable to connect to Supabase. Please try again.';
      this.messageType = 'error';

    } finally {
      this.isLoading = false;
    }
  }

  async onForgotPassword(): Promise<void> {
    this.message = '';

    if (this.email.invalid) {
      this.email.markAsTouched();
      this.message = 'Please enter your registered email address first.';
      this.messageType = 'error';
      return;
    }

    this.isLoading = true;

    try {
      const { error } =
        await this.supabaseService.sendPasswordResetEmail(
          this.email.value ?? ''
        );

      if (error) {
        this.message = error.message;
        this.messageType = 'error';
        return;
      }

      this.message =
        'If an account exists for this email, a password-reset link will be sent. Check your inbox and spam folder.';
      this.messageType = 'success';

    } catch (error) {
      console.error('Password recovery error:', error);
      this.message = 'Unable to send the recovery email. Please try again.';

      this.messageType = 'error';

    } finally {
      this.isLoading = false;
    }
  }

  onSignup(): void {
    this.router.navigate(['/signup']);
  }
}
