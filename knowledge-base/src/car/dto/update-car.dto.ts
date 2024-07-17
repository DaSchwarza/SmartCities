import { PartialType } from '@nestjs/mapped-types';
import { CreateCarDto } from './create-car.dto';
import { ChargingPlan } from '../entities/car.entity';

export class UpdateCarDto extends PartialType(CreateCarDto) {
  isParked?: boolean;
  parkedSince?: Date;
  chargingEnabled?: boolean;
  chargingEnabledSince?: Date;
  charging: boolean
  chargingSince?: Date;
  chargingPower?: number;
  chargingPlan?: ChargingPlan;
  departureTime?: Date;
  carNotPluggedIn?: boolean;
  carUnpluggedEarly?: boolean;
}
