
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
  selector: 'app-signup',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule],
  templateUrl: './signup.html',
  styleUrl: './signup.css'
})
export class Signup {
  fullName = new FormControl('', [
    Validators.required,
    Validators.minLength(2)
  ]);

  email = new FormControl('', [
    Validators.required,
    Validators.email
  ]);

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
    private router: Router,
    private supabaseService: SupabaseService
  ) {}

  async onSubmit(): Promise<void> {
    this.message = '';

    if (
      this.fullName.invalid ||
      this.email.invalid ||
      this.password.invalid ||
      this.confirmPassword.invalid
    ) {
      this.message = 'Please complete all fields correctly.';
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
      const { data, error } = await this.supabaseService.signUp(
        this.fullName.value ?? '',
        this.email.value ?? '',
        this.password.value ?? ''
      );

      if (error) {
        this.message = error.message;
        this.messageType = 'error';
        return;
      }

      if (data.user && !data.session) {
        this.message =
          'Account created. Please check your email to confirm your account.';
      } else {
        this.message = 'Your account has been created successfully.';
      }

      this.messageType = 'success';

    } catch (error) {
      this.message = 'Something went wrong. Please try again.';
      this.messageType = 'error';

      console.error('Signup error:', error);

    } finally {
      this.isLoading = false;
    }
  }

  onLogin(): void {
    this.router.navigate(['/login']);
  }
}
