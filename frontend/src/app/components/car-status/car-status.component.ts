import { Component, Input } from '@angular/core';
import { Car } from '../../models/car.model';

@Component({
  selector: 'app-car-status',
  standalone: true,
  imports: [],
  templateUrl: './car-status.component.html',
  styleUrl: './car-status.component.css'
})
export class CarStatusComponent {
  @Input()
  car!: Car;

  referToCalendar() {
    console.log('Opening calendar link: ', this.car.calendarLink);
    window.open(this.car.calendarLink, '_blank');
  }
}
