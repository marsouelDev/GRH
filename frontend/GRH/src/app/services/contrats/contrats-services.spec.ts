import { TestBed } from '@angular/core/testing';

import { ContratsServices } from './contrats-services';

describe('ContratsServices', () => {
  let service: ContratsServices;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(ContratsServices);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
