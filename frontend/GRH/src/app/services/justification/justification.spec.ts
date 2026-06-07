import { TestBed } from '@angular/core/testing';

import { Justification } from './justification';

describe('Justification', () => {
  let service: Justification;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(Justification);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
