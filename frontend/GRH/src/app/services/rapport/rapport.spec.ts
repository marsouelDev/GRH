import { TestBed } from '@angular/core/testing';

import { Rapport } from './rapport';

describe('Rapport', () => {
  let service: Rapport;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(Rapport);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
