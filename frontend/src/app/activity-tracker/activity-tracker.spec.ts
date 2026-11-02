
import { ComponentFixture, TestBed } from '@angular/core/testing';
import { provideRouter } from '@angular/router';

import { ActivityTracker } from './activity-tracker';

describe('ActivityTracker', () => {
  let component: ActivityTracker;
  let fixture: ComponentFixture<ActivityTracker>;

  // Configure the router and create the Activity Tracker component before each test.
  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [ActivityTracker],
      providers: [provideRouter([])],
    }).compileComponents();

    fixture = TestBed.createComponent(ActivityTracker);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  // Verify that the Activity Tracker component is created successfully.
  it('should create', () => {
    expect(component).toBeTruthy();
  });
});