
import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormControl, ReactiveFormsModule, Validators } from '@angular/forms';
import { Router } from '@angular/router';

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

  onSubmit(): void {
    if (this.email.invalid || this.password.invalid) {
      this.email.markAsTouched();
      this.password.markAsTouched();
      alert('Please enter a valid email address and password.');
      return;
    }

    // Authentication will be connected when the backend is ready.
    alert('Login form is ready. Authentication has not been connected yet.');
  }

  onSignup(): void {
    // Navigate to the Signup page.
    window.location.href = '/signup';
  }
}
