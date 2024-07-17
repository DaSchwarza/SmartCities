import { Logger, Module } from '@nestjs/common';
import { PricesService } from './prices.service';
import { MongooseModule } from '@nestjs/mongoose';
import { DynamicPriceSchema } from './entities/dynamicPrice.entity';

@Module({
  imports: [
    MongooseModule.forFeature([{ name: 'DynamicPrice', schema: DynamicPriceSchema }], 'prices'),
  ],
  providers: [PricesService, Logger],
  exports: [PricesService],
})
export class PricesModule {}
