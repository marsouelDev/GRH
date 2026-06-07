import { ComponentFixture, TestBed } from '@angular/core/testing';

import { Administrateur } from './administrateur';

describe('Administrateur', () => {
  let component: Administrateur;
  let fixture: ComponentFixture<Administrateur>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [Administrateur]
    })
    .compileComponents();

    fixture = TestBed.createComponent(Administrateur);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
