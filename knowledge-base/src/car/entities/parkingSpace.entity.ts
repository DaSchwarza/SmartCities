import { Prop, Schema, SchemaFactory } from '@nestjs/mongoose';
import mongoose, { Document, ObjectId, Types } from 'mongoose';
import { ParkingSensor } from './parkingSensor.entity';
import { SmartPlug } from './smartPlug.entity';
import { Transform } from 'class-transformer';

export type ParkingSpaceDocument = ParkingSpace & Document;

@Schema()
export class ParkingSpace {
  @Transform(({ value }) => value.toString())
  _id: ObjectId;
  @Prop({ required: true })
  alias: number;
  @Prop({ type: mongoose.Schema.Types.ObjectId, ref: ParkingSensor.name })
  parkingSensor: ParkingSensor;
  @Prop({ type: mongoose.Schema.Types.ObjectId, ref: SmartPlug.name })
  smartPlug: SmartPlug;
}

export const ParkingSpaceSchema = SchemaFactory.createForClass(ParkingSpace);
