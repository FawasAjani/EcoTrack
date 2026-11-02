
import { Injectable } from '@angular/core';

export interface Activity {
  type: string;
  fuelType: string;
  purpose: string;
  description: string;
  date: string;
  distance: number;
}

@Injectable({
  providedIn: 'root',
})
export class ActivityService {
  private activities: Activity[] = [];

  getActivities(): Activity[] {
    return this.activities;
  }

  addActivity(activity: Activity): void {
    this.activities.push(activity);
  }

  deleteActivity(index: number): void {
    if (index >= 0 && index < this.activities.length) {
      this.activities.splice(index, 1);
    }
  }
}
