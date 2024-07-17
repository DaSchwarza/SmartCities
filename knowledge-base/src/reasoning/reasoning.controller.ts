import { Body, Controller, Logger, Post } from '@nestjs/common';
import { ReasoningService } from './reasoning.service';
import { CreateCarDto } from 'src/car/dto/create-car.dto';

@Controller('reasoning')
export class ReasoningController {
    constructor(
        private readonly reasoningService: ReasoningService,
        private readonly logger: Logger
    ) {}

    @Post('emergency-charge')
    create(@Body() data: {_id: string}) {
      return this.reasoningService.emergencyCharge(data._id);
    }
}
