
import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { firstValueFrom } from 'rxjs';
import { SupabaseService } from '../supabase.service';

export interface DashboardSummary {
  total_food_co2e: number;
  total_activity_co2: number;
  total_activity_co2e: number;
  total_electricity_co2: number;
  total_co2: number;
  total_co2e: number;

  today_food_co2e: number;
  today_activity_co2: number;
  today_activity_co2e: number;
  today_electricity_co2: number;
  today_co2: number;
  today_co2e: number;

  weekly_food_co2e: number;
  weekly_activity_co2: number;
  weekly_activity_co2e: number;
  weekly_electricity_co2: number;
  weekly_co2: number;
  weekly_co2e: number;

  uncalculated_activities: number;
  ambiguous_activities: number;
  today_uncalculated_activities: number;
  weekly_uncalculated_activities: number;
}

export interface DashboardPeriod {
  today: string;
  week_start: string;
  week_end: string;
}

export interface DailyEmissions {
  date: string;
  food_co2e: number;
  activity_co2: number;
  activity_co2e: number;
  electricity_co2: number;
  total_co2: number;
  total_co2e: number;
}

interface DashboardApiResponse {
  status: string;
  message?: string;
  period?: DashboardPeriod;
  summary?: DashboardSummary;
  weekly_breakdown?: DailyEmissions[];
}

export interface DashboardData {
  period: DashboardPeriod;
  summary: DashboardSummary;
  weekly_breakdown: DailyEmissions[];
}

@Injectable({
  providedIn: 'root'
})
export class DashboardService {
  private readonly apiUrl =
    'http://127.0.0.1:5000/api/dashboard';

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

  private getLocalDate(): string {
    const today = new Date();

    const year = today.getFullYear();
    const month = String(today.getMonth() + 1).padStart(2, '0');
    const day = String(today.getDate()).padStart(2, '0');

    return `${year}-${month}-${day}`;
  }

  async getDashboardSummary(
    today: string = this.getLocalDate()
  ): Promise<DashboardData> {
    const headers = await this.getHeaders();

    const response = await firstValueFrom(
      this.http.get<DashboardApiResponse>(
        `${this.apiUrl}/summary`,
        {
          headers,
          params: { today }
        }
      )
    );

    if (
      response.status !== 'success' ||
      !response.summary ||
      !response.period ||
      !response.weekly_breakdown
    ) {
      throw new Error(
        response.message ||
        'Unable to retrieve the Dashboard summary.'
      );
    }

    return {
      period: response.period,
      summary: response.summary,
      weekly_breakdown: response.weekly_breakdown
    };
  }
}
