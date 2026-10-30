import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import {
  FormControl,
  ReactiveFormsModule,
  Validators
} from '@angular/forms';
import { Router } from '@angular/router';

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

  constructor(private router: Router) {}

  onSubmit(): void {

    this.message = '';

    // Check whether all fields are valid
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

    // Check whether passwords match
    if (this.password.value !== this.confirmPassword.value) {
      this.message = 'Your passwords do not match.';
      this.messageType = 'error';
      return;
    }

    // Display success message
    this.message =
      'Signup form is ready. Account creation is not connected yet.';
    this.messageType = 'success';
  }

  onLogin(): void {
    this.router.navigate(['/login']);
  }
}