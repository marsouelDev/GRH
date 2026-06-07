import { ComponentFixture, TestBed } from '@angular/core/testing';

import { Justification } from './justification';

describe('Justification', () => {
  let component: Justification;
  let fixture: ComponentFixture<Justification>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [Justification]
    })
    .compileComponents();

    fixture = TestBed.createComponent(Justification);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
