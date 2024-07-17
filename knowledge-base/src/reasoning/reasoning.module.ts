import { forwardRef, Logger, Module } from '@nestjs/common';
import { ReasoningService } from './reasoning.service';
import { CarModule } from 'src/car/car.module';
import { ConnectorModule } from 'src/connector/connector.module';
import { PricesModule } from 'src/prices/prices.module';
import { ReasoningController } from './reasoning.controller';

@Module({
  imports: [
    CarModule,
    forwardRef(() => ConnectorModule),
    PricesModule
  ],
  providers: [ReasoningService, Logger],
  exports: [ReasoningService],
  controllers: [ReasoningController],
})
export class ReasoningModule {}
