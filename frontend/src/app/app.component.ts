import { Component, OnInit } from '@angular/core';
import { RouterOutlet } from '@angular/router';
import { CarStatusComponent } from './components/car-status/car-status.component';
import { Car } from './models/car.model';
import { CarService } from './services/car.service';
import { CommonModule } from '@angular/common';
import { CarActionComponent } from './components/car-action/car-action.component';
import { ChargingTimelineComponent } from './components/charging-timeline/charging-timeline.component';
import { EnergyPriceChartComponent } from './components/energy-price-chart/energy-price-chart.component';
import { SpinnerComponent } from './components/spinner/spinner.component';
import { interval } from 'rxjs';
import { switchMap } from 'rxjs/operators';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [RouterOutlet, CarStatusComponent, CarActionComponent, CommonModule, ChargingTimelineComponent, EnergyPriceChartComponent, SpinnerComponent],
  templateUrl: './app.component.html',
  styleUrl: './app.component.css'
})
export class AppComponent implements OnInit {
  cars: Car[] = [];

  constructor(private carService: CarService) {}

  ngOnInit() {
    interval(2000) // Emit every 2 seconds
      .pipe(
        switchMap(() => this.carService.getCarDetails()) // Switch to the getCarDetails observable
      )
      .subscribe({
        next: (cars) => this.cars = cars,
        error: (error) => console.error('Failed to fetch cars', error)
      });
  }
}