import { Module } from '@nestjs/common';
import { MongooseModule } from '@nestjs/mongoose';
import { CarService } from './car.service';
import { CarController } from './car.controller';
import { CarSchema } from './entities/car.entity';
import { ParkingSpaceSchema } from './entities/parkingSpace.entity';
import { SmartPlugSchema } from './entities/smartPlug.entity';
import { ParkingSensorSchema } from './entities/parkingSensor.entity';

@Module({
  imports: [
    MongooseModule.forFeature([{ name: 'SmartPlug', schema: SmartPlugSchema }], 'knowledge'),
    MongooseModule.forFeature([{ name: 'ParkingSensor', schema: ParkingSensorSchema }], 'knowledge'),
    MongooseModule.forFeature([{ name: 'ParkingSpace', schema: ParkingSpaceSchema }], 'knowledge'),
    MongooseModule.forFeature([{ name: 'Car', schema: CarSchema }], 'knowledge'),
  ],
  controllers: [CarController],
  providers: [CarService],
  exports: [CarService],
})
export class CarModule {}
