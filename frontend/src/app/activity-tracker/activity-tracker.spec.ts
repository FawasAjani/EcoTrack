import { ComponentFixture, TestBed } from '@angular/core/testing';
import { provideRouter } from '@angular/router';
import { describe, it, expect, beforeEach } from 'vitest';
import { ActivityTracker } from './activity-tracker';
import { ActivityService } from '../services/activity';

describe('ActivityTracker', () => {
  let component: ActivityTracker;
  let fixture: ComponentFixture<ActivityTracker>;

  // Provide predictable activity data without calling the real backend.
  const mockActivityService = {
    getActivities: async () => [],
    addActivity: async (activity: any) => activity,
    updateActivity: async (id: string, activity: any) => activity,
    deleteActivity: async () => undefined
  };

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [ActivityTracker],
      providers: [
        provideRouter([]),
        {
          provide: ActivityService,
          useValue: mockActivityService
        }
      ]
    }).compileComponents();

    fixture = TestBed.createComponent(ActivityTracker);
    component = fixture.componentInstance;

    fixture.detectChanges();
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});