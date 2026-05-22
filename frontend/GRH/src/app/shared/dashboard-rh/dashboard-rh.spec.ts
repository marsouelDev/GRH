import { ComponentFixture, TestBed } from '@angular/core/testing';

import { DashboardRH } from './dashboard-rh';

describe('DashboardRH', () => {
  let component: DashboardRH;
  let fixture: ComponentFixture<DashboardRH>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [DashboardRH]
    })
    .compileComponents();

    fixture = TestBed.createComponent(DashboardRH);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
