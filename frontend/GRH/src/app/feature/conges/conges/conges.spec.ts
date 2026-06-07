import { ComponentFixture, TestBed } from '@angular/core/testing';

import { CongeComponent } from './conges';

describe('Conges', () => {
  let component: CongeComponent;
  let fixture: ComponentFixture<CongeComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [CongeComponent],
    }).compileComponents();

    fixture = TestBed.createComponent(CongeComponent);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
