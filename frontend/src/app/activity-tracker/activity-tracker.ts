import { DecimalPipe } from '@angular/common';
import { ChangeDetectorRef, Component, OnInit } from '@angular/core';
import { RouterLink } from '@angular/router';
import { FormsModule } from '@angular/forms';
import { Activity, ActivityService } from '../services/activity';

@Component({
  selector: 'app-activity-tracker',
  standalone: true,
  imports: [RouterLink, FormsModule, DecimalPipe],
  templateUrl: './activity-tracker.html',
  styleUrl: './activity-tracker.css'
})
export class ActivityTracker implements OnInit {
  activityType = '';
  fuelType = '';
  purpose = '';
  description = '';
  activityDate = '';
  distance: number | null = null;

  activities: Activity[] = [];
  isLoading = false;
  errorMessage = '';

  constructor(
    private activityService: ActivityService,
    private changeDetector: ChangeDetectorRef
  ) {}

  async ngOnInit(): Promise<void> {
    await this.loadActivities();
  }

  // Retrieve activities belonging to the logged-in user.
  async loadActivities(): Promise<void> {
    this.isLoading = true;
    this.errorMessage = '';
    this.changeDetector.markForCheck();

    try {
      this.activities = await this.activityService.getActivities();
    } catch (error) {
      console.error('Unable to load activities:', error);
      this.errorMessage = 'Unable to load activities. Please try again.';
    } finally {
      this.isLoading = false;
      this.changeDetector.markForCheck();
    }
  }

  // Validate and save a new activity.
  async addActivity(): Promise<void> {
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
      fuelType: this.activityType === 'Car'
        ? this.fuelType
        : 'Not specified',
      purpose: this.purpose,
      description: this.description.trim(),
      date: this.activityDate,
      distance: this.distance,

      // The Flask API calculates these values after submission.
      emissionsKgCo2: null,
      emissionsKgCo2e: null,
      emissionFactor: null,
      emissionFactorUnit: null,
      emissionFactorSource: null,
      emissionFactorYear: null
    };

    try {
      this.errorMessage = '';

      await this.activityService.addActivity(newActivity);

      await this.loadActivities();

      // Reset the form after a successful save.
      this.activityType = '';
      this.fuelType = '';
      this.purpose = '';
      this.description = '';
      this.activityDate = '';
      this.distance = null;

      this.changeDetector.markForCheck();

    } catch (error: any) {
      console.error('Unable to save activity:', error);

      // Display the actual error returned by the Flask API.
      const backendMessage = error?.error?.message;

      this.errorMessage = backendMessage
        ? `Unable to save activity: ${backendMessage}`
        : 'Unable to save activity. Please check the backend terminal for details.';

      this.changeDetector.markForCheck();
    }
  }

  // Delete an activity after user confirmation.
  async deleteActivity(index: number): Promise<void> {
    const activity = this.activities[index];

    if (!activity?.id) {
      this.errorMessage = 'Unable to identify the activity to delete.';
      this.changeDetector.markForCheck();
      return;
    }

    const confirmed = confirm(
      'Are you sure you want to delete this activity?'
    );

    if (!confirmed) {
      return;
    }

    try {
      this.errorMessage = '';

      await this.activityService.deleteActivity(activity.id);

      this.activities = this.activities.filter(
        item => item.id !== activity.id
      );

    } catch (error) {
      console.error('Unable to delete activity:', error);
      this.errorMessage = 'Unable to delete activity. Please try again.';
    } finally {
      this.changeDetector.markForCheck();
    }
  }
}
