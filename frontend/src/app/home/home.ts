
import { Component, OnInit, ChangeDetectorRef } from '@angular/core';
import { RouterLink } from '@angular/router';
import {
  DashboardService,
  DashboardSummary
} from '../services/dashboard.service';

@Component({
  selector: 'app-home',
  standalone: true,
  imports: [RouterLink],
  templateUrl: './home.html',
  styleUrl: './home.css'
})
export class Home implements OnInit {
  summary: DashboardSummary | null = null;
  isLoading = true;
  errorMessage = '';

  constructor(
    private dashboardService: DashboardService,
    private changeDetectorRef: ChangeDetectorRef
  ) {}

  ngOnInit(): void {
    this.loadDashboard();
  }

  async loadDashboard(): Promise<void> {
    this.isLoading = true;
    this.errorMessage = '';

    try {
      const data = await this.dashboardService.getDashboardSummary();
      this.summary = data.summary;
    } catch (error) {
      console.error('Error loading Dashboard data:', error);

      this.errorMessage = error instanceof Error
        ? error.message
        : 'Unable to load Dashboard data.';
    } finally {
      this.isLoading = false;
      this.changeDetectorRef.detectChanges();
    }
  }

  formatEmissions(value: number): string {
    return `${Number(value).toFixed(2)} kg`;
  }
}
