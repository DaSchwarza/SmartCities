import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ChargingTimelineComponent } from './charging-timeline.component';

describe('ChargingTimelineComponent', () => {
  let component: ChargingTimelineComponent;
  let fixture: ComponentFixture<ChargingTimelineComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [ChargingTimelineComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(ChargingTimelineComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
