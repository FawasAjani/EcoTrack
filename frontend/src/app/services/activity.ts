
import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { firstValueFrom } from 'rxjs';
import { SupabaseService } from '../supabase.service';

export interface Activity {
  id?: string;
  type: string;
  fuelType: string;
  purpose: string;
  description: string;
  date: string;
  distance: number;

  // Calculated emissions returned by the Flask API.
  emissionsKgCo2: number | null;
  emissionsKgCo2e: number | null;
  emissionFactor: number | null;
  emissionFactorUnit: string | null;
  emissionFactorSource: string | null;
  emissionFactorYear: number | null;
}

interface ActivityApiRecord {
  id: string;
  category: string;
  fuel_type?: string;
  purpose?: string;
  description: string;
  activity_date: string;
  quantity: number | string;
  emissions_kg_co2?: number | null;
  emissions_kg_co2e?: number | null;
  emission_factor?: number | null;
  emission_factor_unit?: string | null;
  emission_factor_source?: string | null;
  emission_factor_year?: number | null;
}

interface ActivityApiResponse {
  status: string;
  message?: string;
  activities?: ActivityApiRecord[];
  activity?: ActivityApiRecord;
}

@Injectable({
  providedIn: 'root',
})
export class ActivityService {
  private readonly apiUrl = 'http://127.0.0.1:5000/api/activities';

  private activities: Activity[] = [];

  constructor(
    private http: HttpClient,
    private supabaseService: SupabaseService
  ) {}

  // Retrieve the current user's token for authenticated API requests.
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

  // Convert the database activity structure into the frontend structure.
  private mapActivity(activity: ActivityApiRecord): Activity {
    return {
      id: activity.id,
      type: activity.category,
      fuelType: activity.fuel_type || 'Not specified',
      purpose: activity.purpose || '',
      description: activity.description,
      date: activity.activity_date,
      distance: Number(activity.quantity),

      emissionsKgCo2: activity.emissions_kg_co2 ?? null,
      emissionsKgCo2e: activity.emissions_kg_co2e ?? null,
      emissionFactor: activity.emission_factor ?? null,
      emissionFactorUnit: activity.emission_factor_unit ?? null,
      emissionFactorSource: activity.emission_factor_source ?? null,
      emissionFactorYear: activity.emission_factor_year ?? null
    };
  }

  // Load activities belonging to the authenticated user.
  async getActivities(): Promise<Activity[]> {
    const headers = await this.getHeaders();

    const response = await firstValueFrom(
      this.http.get<ActivityApiResponse>(this.apiUrl, { headers })
    );

    this.activities = (response.activities || []).map(
      activity => this.mapActivity(activity)
    );

    return this.activities;
  }

  // Create a new activity in the Supabase database.
  async addActivity(activity: Activity): Promise<Activity> {
    const headers = await this.getHeaders();

    const payload = {
      category: activity.type,
      fuel_type: activity.fuelType,
      purpose: activity.purpose,
      description: activity.description,
      activity_date: activity.date,
      quantity: activity.distance,
      unit: 'km'
    };

    const response = await firstValueFrom(
      this.http.post<ActivityApiResponse>(
        this.apiUrl,
        payload,
        { headers }
      )
    );

    if (!response.activity) {
      throw new Error('The activity was not returned by the server.');
    }

    const savedActivity = this.mapActivity(response.activity);

    this.activities = [...this.activities, savedActivity];

    return savedActivity;
  }

  // Update an existing activity in the database.
  async updateActivity(
    activityId: string,
    activity: Partial<Activity>
  ): Promise<Activity> {
    const headers = await this.getHeaders();

    const payload: Record<string, string | number> = {};

    if (activity.type !== undefined) {
      payload['category'] = activity.type;
    }

    if (activity.fuelType !== undefined) {
      payload['fuel_type'] = activity.fuelType;
    }

    if (activity.purpose !== undefined) {
      payload['purpose'] = activity.purpose;
    }

    if (activity.description !== undefined) {
      payload['description'] = activity.description;
    }

    if (activity.date !== undefined) {
      payload['activity_date'] = activity.date;
    }

    if (activity.distance !== undefined) {
      payload['quantity'] = activity.distance;
    }

    const response = await firstValueFrom(
      this.http.put<ActivityApiResponse>(
        `${this.apiUrl}/${activityId}`,
        payload,
        { headers }
      )
    );

    if (!response.activity) {
      throw new Error('The updated activity was not returned by the server.');
    }

    const updatedActivity = this.mapActivity(response.activity);

    this.activities = this.activities.map(item =>
      item.id === activityId ? updatedActivity : item
    );

    return updatedActivity;
  }

  // Delete an activity from the database.
  async deleteActivity(activityId: string): Promise<void> {
    const headers = await this.getHeaders();

    await firstValueFrom(
      this.http.delete<ActivityApiResponse>(
        `${this.apiUrl}/${activityId}`,
        { headers }
      )
    );

    this.activities = this.activities.filter(
      activity => activity.id !== activityId
    );
  }
}
