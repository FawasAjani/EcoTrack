
import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { firstValueFrom } from 'rxjs';
import { SupabaseService } from '../supabase.service';

export interface ElectricityEntry {
  id: string;
  user_id: string;
  quantity_kwh: number;
  activity_date: string;
  emissions_kg_co2: number;
  emission_factor_snapshot: number;
  emission_factor_unit: string;
  dataset_name_snapshot: string;
  dataset_version_snapshot: string;
  factor_year: number;
  country_model_snapshot: string;
  created_at: string;
}

export interface ElectricityEntryRequest {
  quantity_kwh: number;
  activity_date?: string;
}

interface ElectricityApiResponse {
  status: string;
  message?: string;
  entry?: ElectricityEntry;
  electricity_entries?: ElectricityEntry[];
  count?: number;
}

@Injectable({
  providedIn: 'root'
})
export class ElectricityService {
  private readonly apiUrl =
    'http://127.0.0.1:5000/api/electricity';

  constructor(
    private http: HttpClient,
    private supabaseService: SupabaseService
  ) {}

  private async getHeaders(): Promise<HttpHeaders> {
    const token = await this.supabaseService.getAccessToken();

    if (!token) {
      throw new Error(
        'Your session has expired. Please log in again.'
      );
    }

    return new HttpHeaders({
      Authorization: `Bearer ${token}`,
      'Content-Type': 'application/json'
    });
  }

  async getElectricityEntries(): Promise<ElectricityEntry[]> {
    const headers = await this.getHeaders();

    const response = await firstValueFrom(
      this.http.get<ElectricityApiResponse>(
        `${this.apiUrl}/entries`,
        { headers }
      )
    );

    if (response.status !== 'success') {
      throw new Error(
        response.message || 'Unable to retrieve electricity history.'
      );
    }

    return response.electricity_entries || [];
  }

  async createElectricityEntry(
    entry: ElectricityEntryRequest
  ): Promise<ElectricityEntry> {
    const headers = await this.getHeaders();

    const response = await firstValueFrom(
      this.http.post<ElectricityApiResponse>(
        `${this.apiUrl}/entries`,
        entry,
        { headers }
      )
    );

    if (response.status !== 'success' || !response.entry) {
      throw new Error(
        response.message || 'Unable to save electricity entry.'
      );
    }

    return response.entry;
  }

  async deleteElectricityEntry(entryId: string): Promise<void> {
    const headers = await this.getHeaders();

    const response = await firstValueFrom(
      this.http.delete<ElectricityApiResponse>(
        `${this.apiUrl}/entries/${encodeURIComponent(entryId)}`,
        { headers }
      )
    );

    if (response.status !== 'success') {
      throw new Error(
        response.message || 'Unable to delete electricity entry.'
      );
    }
  }
}
