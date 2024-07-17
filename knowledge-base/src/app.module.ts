import { Module } from '@nestjs/common';
import { ConfigModule } from '@nestjs/config';
import { MongooseModule } from '@nestjs/mongoose';
import { CarModule } from './car/car.module';
import { ConnectorModule } from './connector/connector.module';
import { ReasoningModule } from './reasoning/reasoning.module';
import { PricesModule } from './prices/prices.module';

@Module({
  imports: [
    ConfigModule.forRoot({
      envFilePath: '../.env'
    }),
    MongooseModule.forRoot(process.env.MONGO_URI, {
      dbName: process.env.KNOWLEDGE_DATABASE,
      connectionName: 'knowledge',
    }),
    MongooseModule.forRoot(process.env.MONGO_URI, {
      dbName: process.env.PRICES_DATABASE,
      connectionName: 'prices',
    }),
    CarModule,
    ConnectorModule,
    ReasoningModule,
    PricesModule
  ]
})
export class AppModule {}
