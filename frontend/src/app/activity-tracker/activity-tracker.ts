
import { ChangeDetectorRef, Component, OnInit } from '@angular/core';
import { RouterLink } from '@angular/router';
import { FormsModule } from '@angular/forms';
import { Activity, ActivityService } from '../services/activity';

@Component({
  selector: 'app-activity-tracker',
  standalone: true,
  imports: [RouterLink, FormsModule],
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
      distance: this.distance
    };

    try {
      this.errorMessage = '';
      await this.activityService.addActivity(newActivity);

      await this.loadActivities();

      this.activityType = '';
      this.fuelType = '';
      this.purpose = '';
      this.description = '';
      this.activityDate = '';
      this.distance = null;

      this.changeDetector.markForCheck();
    } catch (error) {
      console.error('Unable to save activity:', error);
      this.errorMessage = 'Unable to save activity. Please try again.';
      this.changeDetector.markForCheck();
    }
  }

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
