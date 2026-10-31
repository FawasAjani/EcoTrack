import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ActivityTracker } from './activity-tracker';

describe('ActivityTracker', () => {
  let component: ActivityTracker;
  let fixture: ComponentFixture<ActivityTracker>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [ActivityTracker],
    }).compileComponents();

    fixture = TestBed.createComponent(ActivityTracker);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
