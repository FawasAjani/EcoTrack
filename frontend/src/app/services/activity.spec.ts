
import { TestBed } from '@angular/core/testing';

import { ActivityService } from './activity';

describe('ActivityService', () => {
  let service: ActivityService;

  // Configure the testing environment and retrieve the ActivityService instance.
  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(ActivityService);
  });

  // Verify that Angular successfully creates the ActivityService.
  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
