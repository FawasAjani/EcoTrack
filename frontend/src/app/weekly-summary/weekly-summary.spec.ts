import { ComponentFixture, TestBed } from '@angular/core/testing';

import { WeeklySummary } from './weekly-summary';

describe('WeeklySummary', () => {
  let component: WeeklySummary;
  let fixture: ComponentFixture<WeeklySummary>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [WeeklySummary],
    }).compileComponents();

    fixture = TestBed.createComponent(WeeklySummary);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
