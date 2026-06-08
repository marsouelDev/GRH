import { TestBed } from '@angular/core/testing';

import { Rh } from './rh';

describe('Rh', () => {
  let service: Rh;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(Rh);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
