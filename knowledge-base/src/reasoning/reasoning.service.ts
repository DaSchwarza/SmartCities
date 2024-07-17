import { Injectable, Logger } from '@nestjs/common';
import { CarService } from 'src/car/car.service';
import { Car, ChargingPlan } from 'src/car/entities/car.entity';
import { ConnectorService } from 'src/connector/connector.service';
import { PricesService } from 'src/prices/prices.service';

@Injectable()
export class ReasoningService {
    constructor(
        private readonly carService: CarService,
        private readonly connectorService: ConnectorService,
        private readonly priceService: PricesService,
        private readonly logger: Logger,
    ) {}

    async newParkingOccupation(parkingSpaceId: number, occupied: boolean) {        
        // Get car from parking space
        try {
            const car: Car = await this.carService.getCarByParkingSpaceId(parkingSpaceId);
    
            const previousOccupation = car.isParked;
    
            if (previousOccupation == occupied) {
                return;
            }

            // update car
            car.isParked = occupied;
            car.parkedSince = occupied ? new Date() : null;
            this.carService.update(car._id.toString(), car);
    
            // generate new plan if car arrived or system started
            if (
                previousOccupation == undefined ||
                (previousOccupation == false && occupied == true)
            ) {
                this.logger.log(`[${parkingSpaceId}] Car arrived`);
                return this.generateContext(car);
            }
            this.logger.log(`[${parkingSpaceId}] Car left`);
        } catch (error) {
            this.logger.error(`[${parkingSpaceId}] Error during parking occupation update: ${error}`);
        }
    }

    async newChargingStatus(parkingSpaceId: number, chargingEnabled: boolean) {
        this.logger.log(`[${parkingSpaceId}] New charging status: ${chargingEnabled}`);
        
        // Get car from parking space
        const car: Car = await this.carService.getCarByParkingSpaceId(parkingSpaceId);

        // update car
        car.chargingEnabled = chargingEnabled;
        car.chargingEnabledSince = chargingEnabled ? new Date() : null;
        this.carService.update(car._id.toString(), car);
    }

    async newChargingPower(parkingSpaceId: number, power: number) {
        this.logger.log(`[${parkingSpaceId}] New charging power: ${power}`);
        
        // Get car from parking space
        const car: Car = await this.carService.getCarByParkingSpaceId(parkingSpaceId);

        // check if power deviates from plan if charging is enabled
        if (car.chargingEnabled) {
            this.checkCharging(car, power);
        }
        car.chargingPower = power;

        // first charging power value
        if (!car.charging && power > 0) {
            car.charging = true;
            car.chargingSince = new Date();
        } else if (power >= 0) {
            // charging is still enabled but stopped
            if (car.charging && car.chargingEnabled) {
                this.logger.error(`[${car.parkingSpace.alias}] Car was unplugged while charging was enabled`);
                car.carUnpluggedEarly = true;
            }
            // car is not charging anymore
            car.charging = false;
            car.chargingSince = null;
        }
        this.carService.update(car._id.toString(), car);
    }

    async newChargingPlan(carId: string, plan: ChargingPlan) {
        this.logger.log(`[${carId}] New charging plan: ${JSON.stringify(plan)}`);
        
        // Get car from parking space
        const car: Car = await this.carService.findOne(carId);

        // update car
        car.chargingPlan = plan;
        this.carService.update(car._id.toString(), car);
    }

    async newUpcomingEvents(licensePlate: string, events: {start: Date, end: Date}[]) {
        // Get car from parking space
        const car: Car = await this.carService.getCarByLicensePlate(licensePlate);

        if(!car) {
            this.logger.error(`[${licensePlate}] Car not found`);
            return;
        }

        const currentTime = new Date();
        const firstEventStart = new Date(events[0].start);
        const secondEventStart = new Date(events[1].start);

        let departureTime: Date;

        // car is back early from first event
        if (currentTime >= firstEventStart && car.isParked) {
            departureTime = secondEventStart;
        } else {
            departureTime = firstEventStart;
        }

        this.logger.log(`[${licensePlate}] New departure time: ${departureTime}`);
        
        // check if departure time changed
        if (car.departureTime == departureTime) {
            return;
        }

        // update car
        car.departureTime = departureTime;
        this.carService.update(car._id.toString(), car);

        // generate new plan if departure time changed
        this.generateContext(car);
    }

    async checkCharging(car: Car, power: number) {
        const pluggedMinutes = ((new Date).getTime() - car.chargingEnabledSince.getTime()) / 60000;
        // car is not charging if power is 0
        if (power == 0 && pluggedMinutes > 5 && !car.carNotPluggedIn
        ) {
            this.logger.error(`[${car.parkingSpace.alias}] Car was not plugged in`);
            car.carNotPluggedIn = true;
        }
    }

    async generateContext(car: Car) {
        this.logger.log(`[${car.parkingSpace.alias}] Generating new context`);

        if (!car.departureTime) {
            this.logger.error(`[${car.parkingSpace.alias}] No departure time set yet`);
            return;
        }

        const prices = await this.priceService.getTodaysPrices();
        // plug maximum is 4kW, interval is 5min, start Soc is 20%, target is 80%
        const required_cycles = Math.ceil(((0.1 * car.batteryCapacity) / 4) * 12)
        const formattedCar = {
            car_id: car.licensePlate,
            required_cycles,
            deadline: car.departureTime,
            parkingSpace: car.parkingSpace.alias
        }
        const context = {
            car: formattedCar,
            prices: prices
        }
        this.logger.log(`[${car.parkingSpace.alias}] Generated new context: ${JSON.stringify(formattedCar)}`);
        this.connectorService.publishToBroker('/standardized/plan/create', context);
    }

    async emergencyCharge(carId: string) {
        this.logger.log(`[${carId}] Emergency charging initiated`);
        const car: Car = await this.carService.findOne(carId);

        // update car
        car.emergencyCharging = true;
        this.carService.update(car._id.toString(), car);

        const prices = await this.priceService.getTodaysPrices();
        console.log(prices);
        // plug maximum is 4kW, interval is 5min, start Soc is 20%, target is 80%
        const required_cycles = Math.ceil(((0.1 * car.batteryCapacity) / 4) * 12)
        // set depature time to now + required_cycles
        const deadline = new Date();
        deadline.setMinutes(deadline.getMinutes() + required_cycles * 5);
        // round to next 5min slot
        const minutesToAdd = (5 - (deadline.getMinutes() % 5) % 5);
        deadline.setMinutes(deadline.getMinutes() + minutesToAdd, 0, 0);

        const formattedCar = {
            car_id: car.licensePlate,
            required_cycles,
            deadline,
            parkingSpace: car.parkingSpace.alias
        }
        const context = {
            car: formattedCar,
            prices: prices
        }
        this.logger.log(`[${car.parkingSpace.alias}] Generated emergency context: ${JSON.stringify(formattedCar)}`);
        this.connectorService.publishToBroker('/standardized/plan/create', context);
    }
}
