import { Inject, Injectable, Logger } from '@nestjs/common';
import { ClientProxy } from '@nestjs/microservices';

@Injectable()
export class ConnectorService {
    constructor(
        @Inject('MQTT_LISTENER')
        private client: ClientProxy,
    ) {
        client.connect();
    }

    publishToBroker(topic: string, data: any) {
        const formattedData = { data }
        this.client.emit(topic, formattedData);
    }
}
