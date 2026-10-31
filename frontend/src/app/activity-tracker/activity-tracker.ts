
import { Component } from '@angular/core';
import { RouterLink } from '@angular/router';
import { FormsModule } from '@angular/forms';

interface Activity {
  type: string;
  fuelType: string;
  purpose: string;
  description: string;
  date: string;
  distance: number;
}

@Component({
  selector: 'app-activity-tracker',
  standalone: true,
  imports: [RouterLink, FormsModule],
  templateUrl: './activity-tracker.html',
  styleUrl: './activity-tracker.css'
})
export class ActivityTracker {

  activityType = '';
  fuelType = '';
  purpose = '';
  description = '';
  activityDate = '';
  distance: number | null = null;

  activities: Activity[] = [];

  addActivity() {

    if (
      !this.activityType ||
      !this.purpose ||
      !this.activityDate ||
      this.distance === null ||
      this.distance <= 0 ||
      (this.activityType === 'Car' && !this.fuelType)
    ) {
      alert('Please complete all required fields with valid information.');
      return;
    }

    const newActivity: Activity = {
      type: this.activityType,
      fuelType: this.activityType === 'Car' ? this.fuelType : 'Not specified',
      purpose: this.purpose,
      description: this.description.trim(),
      date: this.activityDate,
      distance: this.distance
    };

    this.activities.push(newActivity);

    this.activityType = '';
    this.fuelType = '';
    this.purpose = '';
    this.description = '';
    this.activityDate = '';
    this.distance = null;
  }

  deleteActivity(index: number) {

    const confirmed = confirm('Are you sure you want to delete this activity?');

    if (confirmed) {
      this.activities.splice(index, 1);
    }
  }

}
