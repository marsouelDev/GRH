import { ComponentFixture, TestBed } from '@angular/core/testing';

import { DashboardRh } from './dashboard-rh';

describe('DashboardRh', () => {
  let component: DashboardRh;
  let fixture: ComponentFixture<DashboardRh>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [DashboardRh]
    })
    .compileComponents();

    fixture = TestBed.createComponent(DashboardRh);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
