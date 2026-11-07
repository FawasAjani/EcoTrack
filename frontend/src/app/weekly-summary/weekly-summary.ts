
import { Component, OnInit } from '@angular/core';
import { RouterLink } from '@angular/router';
import { Activity, ActivityService } from '../services/activity';

@Component({
  selector: 'app-weekly-summary',
  standalone: true,
  imports: [RouterLink],
  templateUrl: './weekly-summary.html',
  styleUrl: './weekly-summary.css'
})
export class WeeklySummary implements OnInit {
  activities: Activity[] = [];
  isLoading = false;
  errorMessage = '';

  constructor(private activityService: ActivityService) {}

  async ngOnInit(): Promise<void> {
    await this.loadActivities();
  }

  async loadActivities(): Promise<void> {
    this.isLoading = true;
    this.errorMessage = '';

    try {
      this.activities = await this.activityService.getActivities();
    } catch (error) {
      console.error('Unable to load weekly activities:', error);
      this.errorMessage = 'Unable to load your activities. Please try again.';
    } finally {
      this.isLoading = false;
    }
  }

  get weeklyActivities(): Activity[] {
    const today = new Date();
    const startOfWeek = new Date(today);

    // Calculate Monday as the beginning of the current week.
    const day = (today.getDay() + 6) % 7;
    startOfWeek.setDate(today.getDate() - day);
    startOfWeek.setHours(0, 0, 0, 0);

    const endOfWeek = new Date(startOfWeek);
    endOfWeek.setDate(startOfWeek.getDate() + 7);

    return this.activities.filter(activity => {
      const activityDate = new Date(`${activity.date}T00:00:00`);
      return activityDate >= startOfWeek && activityDate < endOfWeek;
    });
  }

  get weeklyActivityCount(): number {
    return this.weeklyActivities.length;
  }
}
