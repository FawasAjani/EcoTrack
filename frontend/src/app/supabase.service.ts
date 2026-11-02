
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

  async signIn(email: string, password: string) {
    const { data, error } =
      await this.supabase.auth.signInWithPassword({
        email,
        password
      });

    return { data, error };
  }

  async signOut() {
    const { error } = await this.supabase.auth.signOut();
    return { error };
  }

  async sendPasswordResetEmail(email: string) {
    const { data, error } =
      await this.supabase.auth.resetPasswordForEmail(email, {
        redirectTo: 'http://localhost:4200/reset-password'
      });

    return { data, error };
  }

  async updatePassword(newPassword: string) {
    const { data, error } =
      await this.supabase.auth.updateUser({
        password: newPassword
      });

    return { data, error };
  }
}
