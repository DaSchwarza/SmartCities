import { ComponentFixture, TestBed } from '@angular/core/testing';

import { EnergyPriceChartComponent } from './energy-price-chart.component';

describe('EnergyPriceChartComponent', () => {
  let component: EnergyPriceChartComponent;
  let fixture: ComponentFixture<EnergyPriceChartComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [EnergyPriceChartComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(EnergyPriceChartComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
