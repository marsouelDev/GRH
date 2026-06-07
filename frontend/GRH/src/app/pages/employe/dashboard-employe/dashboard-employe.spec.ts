import { ComponentFixture, TestBed } from '@angular/core/testing';

import { DashboardEmploye } from './dashboard-employe';

describe('DashboardEmploye', () => {
  let component: DashboardEmploye;
  let fixture: ComponentFixture<DashboardEmploye>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [DashboardEmploye]
    })
    .compileComponents();

    fixture = TestBed.createComponent(DashboardEmploye);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
