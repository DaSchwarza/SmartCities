import { Controller, Logger } from '@nestjs/common';
import { Ctx, MessagePattern, MqttContext, Payload } from '@nestjs/microservices';
import { CarPlanDto } from './dto/newPlan.dto';
import { ChargingPlan, ChargingPlanElement } from 'src/car/entities/car.entity';
import { ReasoningService } from 'src/reasoning/reasoning.service';
import { CarService } from 'src/car/car.service';
import { ConnectorService } from './connector.service';

@Controller('input')
export class ConnectorController {
    constructor(
        private readonly reasoningService: ReasoningService,
        private readonly connectorService: ConnectorService,
        private readonly carService: CarService,
        private readonly logger: Logger
    ) {}

    @MessagePattern('/standardized/parking/+/occupation')
    async handleParkingData(@Payload() data, @Ctx() context: MqttContext) {
        const topic = context.getTopic();
        
        try {
            const macAddress = topic.split('/')[3];
            const parkingSpaceAlias = await this.carService.getParkingSpaceAliasByParkingSensor(macAddress);
            this.reasoningService.newParkingOccupation(parkingSpaceAlias, data.occupied);
        } catch (error) {
            this.logger.error(`Error during parking data handling: ${error}`);
        }
    }

    @MessagePattern('/standardized/parking/+/power')
    async handleChargingInfo(@Payload() data, @Ctx() context: MqttContext) {
        const topic = context.getTopic();

        try {
            const macAddress = topic.split('/')[3];
            const parkingSpaceAlias = await this.carService.getParkingSpaceAliasByPlug(macAddress);
            this.reasoningService.newChargingPower(parkingSpaceAlias, data.power);
        } catch (error) {
            this.logger.error(`Error during parking data handling: ${error}`);
        }
    }

    @MessagePattern('/standardized/parking/+/charging/status')
    async handleChargingStatus(@Payload() data, @Ctx() context: MqttContext) {
        const topic = context.getTopic();

        try {
            const macAddress = topic.split('/')[3];
            const parkingSpaceAlias = await this.carService.getParkingSpaceAliasByPlug(macAddress);
            this.reasoningService.newChargingStatus(parkingSpaceAlias, data.enabled);
        } catch (error) {
            this.logger.error(`Error during parking data handling: ${error}`);
        }
    }

    @MessagePattern('/standardized/plan/created')
    async handleChargingPlan(@Payload() data: CarPlanDto[]) {
        this.logger.log(`Received new charging plans: ${JSON.stringify(data)}`);

        // convert to charging plan object
        data.forEach(async plan => {
            const car = await this.carService.getCarByParkingSpaceId(plan.parkingSpace);

            const chargingPlan: ChargingPlan = new ChargingPlan();
            chargingPlan.createdAt = new Date();
            chargingPlan.planElements = [];

            plan.actions.forEach(action => {
                const chargingPlanElement = new ChargingPlanElement();
                chargingPlanElement.from = new Date(action.start_time);
                chargingPlanElement.to = new Date(action.end_time);
        
                chargingPlan.planElements.push(chargingPlanElement);
            });
            // send charging plan to reasoning service
            this.reasoningService.newChargingPlan(car._id.toString(), chargingPlan);
        });
    }

    @MessagePattern('/standardized/calendar/events/+')
    async handleUpcomingEvents(@Payload() data, @Ctx() context: MqttContext) {
        const topic = context.getTopic();
        const licensePlate = topic.split('/')[4];

        this.logger.log(`[${licensePlate}] Received upcoming events: ${JSON.stringify(data)}`);
        this.reasoningService.newUpcomingEvents(licensePlate, data.events);
    }

    // add context to action
    @MessagePattern('/standardized/execute/+')
    async handleAction(@Payload() data, @Ctx() context: MqttContext) {
        const topic = context.getTopic();
        const parkingSpaceId: number = Number(topic.split('/')[3]);

        // get mac adress
        const macAddress = await this.carService.getPlugMacAddressByParkingSpaceId(parkingSpaceId);
        this.connectorService.publishToBroker(`/standardized/execute/mac/${macAddress}`, { enabled: data.enabled });
    }
}
