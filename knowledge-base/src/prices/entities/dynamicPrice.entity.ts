import { Prop, Schema, SchemaFactory } from '@nestjs/mongoose';
import { Transform } from 'class-transformer';
import { Document, ObjectId } from 'mongoose';

export type DynamicPriceDocument = DynamicPrice & Document;

@Schema()
export class DynamicPrice {
  @Transform(({ value }) => value.toString())
  _id: ObjectId;
  @Prop({ required: true })
  timestamp: Date;
  @Prop({ required: true })
  price: number;
}

export const DynamicPriceSchema = SchemaFactory.createForClass(DynamicPrice);
