import { Injectable, Logger } from '@nestjs/common';
import { InjectModel } from '@nestjs/mongoose';
import { Model } from 'mongoose';
import { DynamicPrice } from './entities/dynamicPrice.entity';

@Injectable()
export class PricesService {
    constructor(
        @InjectModel('DynamicPrice', 'prices')
        private readonly dynamicPriceModel: Model<DynamicPrice>,
        private readonly logger: Logger
    ) {}

    async getTodaysPrices(): Promise<DynamicPrice[]> {
        const date = new Date();
        const minutes = date.getMinutes();
        const last5MinSlot = 5 * Math.floor(minutes / 5);
        date.setMinutes(last5MinSlot, 0, 0);

        this.logger.log(`Fetching dynamic prices from ${date}`);
        const query = {
            timestamp: {
                $gte: date
            }
        }
        return this.dynamicPriceModel.find(query).select('-_id -__v').exec();
    }
}
