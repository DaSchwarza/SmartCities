import { Component, Input } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { Car } from '../../models/car.model';
import { CarService } from '../../services/car.service';

@Component({
  selector: 'app-car-action',
  standalone: true,
  imports: [FormsModule],
  templateUrl: './car-action.component.html',
  styleUrl: './car-action.component.css'
})
export class CarActionComponent {
  @Input()
  car!: Car;

  startSoc = 20;

  constructor(private carService: CarService) {}

  async emergencyCharge(): Promise<void> {
    console.log('Emergency charge');
    const response = await this.carService.emergencyCharge(this.car._id);
    console.log(response)
  }

  async changeStartSoc(startSoC: number): Promise<void> {
    console.log(`Change start SoC to ${this.startSoc}`);
    this.startSoc = startSoC
    const response = await this.carService.changeStartSoc(this.car._id, startSoC);
    console.log(response)
  }
}
