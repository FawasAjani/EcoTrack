
import { ComponentFixture, TestBed } from '@angular/core/testing';
import { provideRouter } from '@angular/router';

import { WeeklySummary } from './weekly-summary';

describe('WeeklySummary', () => {
  let component: WeeklySummary;
  let fixture: ComponentFixture<WeeklySummary>;

  // Configure the router and create the Weekly Summary component before each test.
  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [WeeklySummary],
      providers: [provideRouter([])],
    }).compileComponents();

    fixture = TestBed.createComponent(WeeklySummary);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  // Verify that the Weekly Summary component is created successfully.
  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
