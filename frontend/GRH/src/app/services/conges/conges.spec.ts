import { TestBed } from '@angular/core/testing';

import { Conges } from './conges';

describe('Conges', () => {
  let service: Conges;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(Conges);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
