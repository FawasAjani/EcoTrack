
import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { firstValueFrom } from 'rxjs';
import { SupabaseService } from '../supabase.service';

export interface FoodItem {
  id: string;
  name: string;
  category: string;
  emission_factor_kg_co2e_per_kg: number;
  emission_factor_unit: string;
  dataset_name: string;
  dataset_version: string;
  country_model: string;
  source_indicator: string;
}

interface FoodItemsApiResponse {
  status: string;
  message?: string;
  food_items?: FoodItem[];
  count?: number;
}

export interface FoodEntryRequest {
  food_item_id: string;
  quantity_grams: number;
  activity_date?: string;
}

export interface FoodEntry {
  id: string;
  user_id: string;
  food_item_id: string;
  quantity_grams: number;
  activity_date: string;
  food_name_snapshot: string;
  emissions_kg_co2e: number;
  emission_factor_snapshot: number;
  emission_factor_unit: string;
  dataset_name_snapshot: string;
  dataset_version_snapshot: string;
  country_model_snapshot: string;
  created_at: string;
}

interface FoodEntryApiResponse {
  status: string;
  message?: string;
  entry?: FoodEntry;
}

@Injectable({
  providedIn: 'root'
})
export class FoodService {
  private readonly apiUrl = 'http://127.0.0.1:5000/api/food';

  constructor(
    private http: HttpClient,
    private supabaseService: SupabaseService
  ) {}

  private async getHeaders(): Promise<HttpHeaders> {
    const token = await this.supabaseService.getAccessToken();

    if (!token) {
      throw new Error('Your session has expired. Please log in again.');
    }

    return new HttpHeaders({
      Authorization: `Bearer ${token}`,
      'Content-Type': 'application/json'
    });
  }

  async getFoodItems(): Promise<FoodItem[]> {
    const headers = await this.getHeaders();

    const response = await firstValueFrom(
      this.http.get<FoodItemsApiResponse>(
        `${this.apiUrl}/items`,
        { headers }
      )
    );

    return response.food_items || [];
  }

  async createFoodEntry(
    entry: FoodEntryRequest
  ): Promise<FoodEntry> {
    const headers = await this.getHeaders();

    const response = await firstValueFrom(
      this.http.post<FoodEntryApiResponse>(
        `${this.apiUrl}/entries`,
        entry,
        { headers }
      )
    );

    if (!response.entry) {
      throw new Error(
        response.message || 'Unable to save the food entry.'
      );
    }

    return response.entry;
  }
}
