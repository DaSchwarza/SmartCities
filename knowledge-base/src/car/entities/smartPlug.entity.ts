import { Prop, Schema, SchemaFactory } from '@nestjs/mongoose';
import { Transform } from 'class-transformer';
import { Document, ObjectId } from 'mongoose';

export type SmartPlugDocument = SmartPlug & Document;

@Schema()
export class SmartPlug {
  @Transform(({ value }) => value.toString())
  _id: ObjectId;
  @Prop({ required: true })
  alias: number;
  @Prop({ required: true })
  macAddress: string;
}

export const SmartPlugSchema = SchemaFactory.createForClass(SmartPlug);
