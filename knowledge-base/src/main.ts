import { NestFactory } from '@nestjs/core';
import { AppModule } from './app.module';
import { Logger, ValidationPipe } from '@nestjs/common';
import { MicroserviceOptions, Transport } from '@nestjs/microservices';
import { ConfigService } from '@nestjs/config';

async function bootstrap() {
  const app = await NestFactory.create(AppModule);

  app.useGlobalPipes(new ValidationPipe());
  app.useLogger(app.get(Logger));
  
  const configService: ConfigService = app.get(ConfigService);

  // mqtt listener for standardized sensor input
  const mqttService = app.connectMicroservice<MicroserviceOptions>(
    {
      transport: Transport.MQTT,
      options: {
        url: `mqtt://${configService.get("MQTT_BROKER")}:${configService.get("MQTT_PORT")}`,
        username: configService.get("MQTT_USER"),
        password: configService.get("MQTT_PASSWORD"),
      },
    }, {
      inheritAppConfig: true,
    }
  );
  await app.startAllMicroservices()
  await app.listen(3000);
}
bootstrap();
