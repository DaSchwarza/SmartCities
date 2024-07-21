import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { map, Observable } from 'rxjs';
import { Car, TimelineEntry } from '../models/car.model';

@Injectable({
  providedIn: 'root'
})
export class CarService {
  private baseUrl = 'http://localhost:3000'; // Change to your actual backend URL

  constructor(private http: HttpClient) { }

  getCarDetails(): Observable<Car[]> {
    return this.http.get<Car[]>(`${this.baseUrl}/car`).pipe(
      map((cars: any[]) => cars.map(car => this.transformCar(car)))
    );
  }

  emergencyCharge(carId: string): Promise<any> {
    return this.http.post(`${this.baseUrl}/reasoning/emergency-charge`, { _id: carId }).toPromise();
  }

  changeStartSoc(carId: string, startSoC: number): Promise<any> {
    return this.http.post(`${this.baseUrl}/reasoning/changeStartSoC`, { _id: carId, startSoC }).toPromise();
  }

  private transformCar(carData: any): Car {
    let entries: TimelineEntry[] = [];
    if (carData.chargingPlan) {
      entries = carData.chargingPlan.planElements.map((item: any) => new TimelineEntry('charging', new Date(item.from), new Date(item.to)));
    }
    if (carData.calendarEntries) {
      entries = entries.concat(carData.calendarEntries.map((item: any) => new TimelineEntry('inUse', new Date(item.start), new Date(item.end))));
    }

    const mergedEntries = this.mergeAndCalculateIdle(entries);

    // Create a new Car instance using the constructor
    const car = new Car(
      carData._id,
      carData.licensePlate,
      carData.manufacturer,
      carData.model,
      carData.batteryCapacity,
      carData.calendarLink,
      carData.isParked,
      carData.parkedSince ? new Date(carData.parkedSince) : undefined,
      carData.chargingEnabled,
      carData.chargingEnabledSince ? new Date(carData.chargingEnabledSince) : undefined,
      carData.charging,
      carData.chargingSince ? new Date(carData.chargingSince) : undefined,
      carData.chargingPower,
      carData.chargingPlan, // Assuming some structure for ChargingPlan
      carData.calendarEntries,
      mergedEntries,
      new Date(carData.departureTime),
      carData.carNotPluggedIn,
      carData.carUnpluggedEarly,
      carData.startSoC,
      carData.emergencyCharging,
      carData.planGenerating,
    );

    // Assuming the car class can accept timeline entries after creation,
    // or consider including this in the constructor if frequently used
    car.timelineEntries = mergedEntries;

    return car;
  }

  private mergeAndCalculateIdle(entries: TimelineEntry[]): TimelineEntry[] {
    if (entries.length === 0) {
      return [];
    }

    // Sort entries by start time
    entries.sort((a, b) => a.from.getTime() - b.from.getTime());

    let mergedEntries: TimelineEntry[] = [];
    let now = new Date(); // Get the current time
    let firstEntryStart = new Date(entries[0].from);

    // Add initial idle time from "now" to the first entry's start if there's a gap and "now" is earlier
    if (now < firstEntryStart) {
      mergedEntries.push(new TimelineEntry('idle', now, firstEntryStart));
    }

    let lastEndTime = firstEntryStart;

    entries.forEach((entry, index) => {
      if (entry.from > lastEndTime) {
        // There's a gap between the last end time and the current start time
        mergedEntries.push(new TimelineEntry('idle', lastEndTime, entry.from));
      }
      // push the entry
      mergedEntries.push(new TimelineEntry(entry.type, entry.from, entry.to));


      // Update the last end time
      lastEndTime = new Date(Math.max(lastEndTime.getTime(), entry.to.getTime()));
    });

    return mergedEntries;
  }
}
