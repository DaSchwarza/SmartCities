import { forwardRef, Logger, Module } from '@nestjs/common';
import { ConnectorService } from './connector.service';
import { ConnectorController } from './connector.controller';
import { ConfigModule, ConfigService } from '@nestjs/config';
import { ClientsModule, Transport } from '@nestjs/microservices';
import { ReasoningModule } from 'src/reasoning/reasoning.module';
import { CarModule } from 'src/car/car.module';
import { OutboundResponseSerializer } from './serializer';


@Module({
  imports: [
    // Client for Injection to publish to Broker
    ClientsModule.registerAsync([
      {
        name: 'MQTT_LISTENER',
        imports: [ConfigModule, CarModule],
        useFactory:  (configService: ConfigService) => ({
          transport: Transport.MQTT,
          options: {
            url: `mqtt://${configService.get('MQTT_BROKER')}:${configService.get('MQTT_PORT')}`,
            username: 'local',
            password: 'Stuttgart',
            serializer: new OutboundResponseSerializer()
          },
        }),
        inject: [ConfigService],
      },
    ]),
    forwardRef(() => ReasoningModule),
    CarModule
  ],
  providers: [ConnectorService, Logger],
  exports: [ConnectorService],
  controllers: [ConnectorController]
})
export class ConnectorModule {}
