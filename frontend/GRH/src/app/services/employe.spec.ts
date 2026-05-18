import { TestBed } from '@angular/core/testing';

import { Employe } from './employe';

describe('Employe', () => {
  let service: Employe;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(Employe);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
