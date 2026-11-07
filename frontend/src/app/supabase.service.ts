
import { Injectable } from '@angular/core';
import { createClient, SupabaseClient } from '@supabase/supabase-js';
import { environment } from '../environments/environment';

@Injectable({
  providedIn: 'root'
})
export class SupabaseService {
  supabase: SupabaseClient;

  constructor() {
    this.supabase = createClient(
      environment.supabaseUrl,
      environment.supabaseKey,
      {
        auth: {
          autoRefreshToken: true,
          persistSession: true,
          detectSessionInUrl: true
        }
      }
    );
  }

  // Register a new user.
  async signUp(fullName: string, email: string, password: string) {
    const { data, error } = await this.supabase.auth.signUp({
      email,
      password,
      options: {
        data: { full_name: fullName }
      }
    });

    return { data, error };
  }

  // Sign in using email and password.
  async signIn(email: string, password: string) {
    const { data, error } =
      await this.supabase.auth.signInWithPassword({
        email,
        password
      });

    return { data, error };
  }

  // Retrieve the current authenticated user's access token.
  async getAccessToken(): Promise<string | null> {
    const { data, error } = await this.supabase.auth.getSession();

    if (error) {
      console.error('Unable to retrieve Supabase session:', error);
      return null;
    }

    return data.session?.access_token ?? null;
  }

  // Sign out the current user.
  async signOut() {
    const { error } = await this.supabase.auth.signOut();
    return { error };
  }

  // Send a password recovery email.
  async sendPasswordResetEmail(email: string) {
    const { data, error } =
      await this.supabase.auth.resetPasswordForEmail(email, {
        redirectTo: 'http://localhost:4200/reset-password'
      });

    return { data, error };
  }

  // Update the current user's password.
  async updatePassword(newPassword: string) {
    const { data, error } =
      await this.supabase.auth.updateUser({
        password: newPassword
      });

    return { data, error };
  }
}
