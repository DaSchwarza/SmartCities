import { Serializer, OutgoingResponse } from '@nestjs/microservices';
import { Logger } from '@nestjs/common';

export class OutboundResponseSerializer implements Serializer {

    private readonly logger = new Logger('OutboundResponseIdentitySerializer');

    serialize(value: any): OutgoingResponse {
      return value.data;
    }
}