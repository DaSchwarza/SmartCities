import { Prop, Schema, SchemaFactory } from '@nestjs/mongoose';
import mongoose, { Document, ObjectId } from 'mongoose';
import { ParkingSpace } from './parkingSpace.entity';
import { Transform } from 'class-transformer';

export type CarDocument = Car & Document;

export class ChargingPlan {
  planElements: ChargingPlanElement[];
  createdAt: Date;
}

export class ChargingPlanElement {
  from: Date;
  to: Date;
}

@Schema()
export class Car {
  // Core attributes
  @Transform(({ value }) => value.toString())
  _id: ObjectId;
  @Prop({ required: true })
  licensePlate: string;
  @Prop({ required: true })
  manufacturer: string;
  @Prop({ required: true })
  model: string;
  @Prop({ required: true })
  batteryCapacity: number;
  @Prop({ type: mongoose.Schema.Types.ObjectId, ref: ParkingSpace.name, required: true})
  parkingSpace: ParkingSpace;
  @Prop({ required: true })
  calendarLink: string;

  
  // Reasoning attributes
  @Prop()
  isParked?: boolean;
  @Prop()
  parkedSince?: Date;
  @Prop()
  chargingEnabled?: boolean;
  @Prop()
  chargingEnabledSince?: Date;
  @Prop()
  charging: boolean
  @Prop()
  chargingSince?: Date;
  @Prop()
  chargingPower?: number;
  @Prop()
  chargingPlan?: ChargingPlan;
  @Prop()
  departureTime?: Date;
  @Prop()
  carNotPluggedIn?: boolean;
  @Prop()
  carUnpluggedEarly?: boolean;
  @Prop()
  startSoC?: number;
  @Prop()
  emergencyCharging?: boolean;
  @Prop({ type: Object })
  calendarEntries: any
  @Prop()
  planGenerating: boolean
}

export const CarSchema = SchemaFactory.createForClass(Car);