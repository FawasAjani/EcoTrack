
import { Component } from '@angular/core';
import { RouterLink } from '@angular/router';
import { Activity, ActivityService } from '../services/activity';

@Component({
  selector: 'app-weekly-summary',
  standalone: true,
  imports: [RouterLink],
  templateUrl: './weekly-summary.html',
  styleUrl: './weekly-summary.css'
})
export class WeeklySummary {

  constructor(private activityService: ActivityService) {}

  get activities(): Activity[] {
    return this.activityService.getActivities();
  }

  get weeklyActivities(): Activity[] {
    const today = new Date();
    const startOfWeek = new Date(today);

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
