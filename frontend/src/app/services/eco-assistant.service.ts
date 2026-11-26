import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { firstValueFrom } from 'rxjs';
import { SupabaseService } from '../supabase.service';

export interface EcoRecommendation {
  category: string;
  title: string;
  message: string;
  impact_type: string;
  priority: string;
}

interface EcoAssistantResponse {
  status: string;
  recommendations: EcoRecommendation[];
}

interface EcoChatResponse {
  status: string;
  response: string;
}

@Injectable({
  providedIn: 'root'
})
export class EcoAssistantService {
  private readonly apiUrl =
    'http://127.0.0.1:5000/api/eco-assistant';

  constructor(
    private http: HttpClient,
    private supabaseService: SupabaseService
  ) {}

  private async getHeaders(): Promise<HttpHeaders> {
    const token = await this.supabaseService.getAccessToken();

    if (!token) {
      throw new Error('You must be logged in to use Eco Assistant.');
    }

    return new HttpHeaders({
      Authorization: `Bearer ${token}`
    });
  }

  async getRecommendations(): Promise<EcoRecommendation[]> {
    const headers = await this.getHeaders();

    const response = await firstValueFrom(
      this.http.get<EcoAssistantResponse>(
        `${this.apiUrl}/recommendations`,
        { headers }
      )
    );

    return response.recommendations;
  }

  async sendMessage(message: string): Promise<string> {
    const headers = await this.getHeaders();

    const response = await firstValueFrom(
      this.http.post<EcoChatResponse>(
        `${this.apiUrl}/chat`,
        { message },
        { headers }
      )
    );

    return response.response;
  }
}