import { TestBed } from '@angular/core/testing';

import { PosteServices } from './poste-services';

describe('PosteServices', () => {
  let service: PosteServices;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(PosteServices);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
