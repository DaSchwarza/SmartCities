import { Prop, Schema, SchemaFactory } from '@nestjs/mongoose';
import { Transform } from 'class-transformer';
import { Document, ObjectId } from 'mongoose';

export type ParkingSensorDocument = ParkingSensor & Document;

@Schema()
export class ParkingSensor {
  @Transform(({ value }) => value.toString())
  _id: ObjectId;
  @Prop({ required: true })
  alias: number;
  @Prop({ required: true })
  macAddress: string;
}

export const ParkingSensorSchema = SchemaFactory.createForClass(ParkingSensor);
