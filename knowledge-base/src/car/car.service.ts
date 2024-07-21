import { BadRequestException, Injectable } from '@nestjs/common';
import { InjectModel } from '@nestjs/mongoose';
import { Model } from 'mongoose';
import { CreateCarDto } from './dto/create-car.dto';
import { UpdateCarDto } from './dto/update-car.dto';
import { Car } from './entities/car.entity';
import { ParkingSpace } from './entities/parkingSpace.entity';
import { ParkingSensor } from './entities/parkingSensor.entity';
import { SmartPlug } from './entities/smartPlug.entity';

@Injectable()
export class CarService {
  constructor(
    @InjectModel(Car.name, 'knowledge')
    private readonly carModel: Model<Car>,
    @InjectModel(ParkingSpace.name, 'knowledge')
    private readonly parkingSpaceModel: Model<ParkingSpace>,
    @InjectModel(ParkingSensor.name, 'knowledge')
    private readonly parkingSensorModel: Model<ParkingSensor>,
    @InjectModel(SmartPlug.name, 'knowledge')
    private readonly smartPlugModel: Model<SmartPlug>
  ) {
    // remove all reasoning fields since they might be outdated
    this.removeReasoningFields();
  }

  async create(createCarDto: CreateCarDto) {
    const { parkingSpaceAlias } = createCarDto
    const parkingSpace: ParkingSpace = await this.parkingSpaceModel.findOne({ alias: parkingSpaceAlias });

    // check if another car is already connected to the parking space
    const duplicateCar = await this.carModel.findOne({ parkingSpace: parkingSpace });
    if (duplicateCar) {
      throw new BadRequestException('Parking space is already occupied');
    }

    const car = new this.carModel({
      ...createCarDto,
      parkingSpace: parkingSpace
    });
    car.save();

    return car
      .populate({
        path: 'parkingSpace',
        populate: {
          path: 'smartPlug parkingSensor',
      }})  }

  findAll() {
    return this.carModel
      .find()
      .populate({
        path: 'parkingSpace',
        populate: {
          path: 'smartPlug parkingSensor',
      }})
      .exec();
  }

  findOne(id: string) {
    return this.carModel
      .findById(id)
      .populate({
        path: 'parkingSpace',
        populate: {
          path: 'smartPlug parkingSensor',
      }})
      .exec();
  }

  async update(id: string, updateCarDto: UpdateCarDto) {
    const existingCar = await this.carModel.findById(id);

    if (!existingCar) {
      throw new BadRequestException(`Car with id ${id} not found`);
    }
    const updatedCar =  await this.carModel.findByIdAndUpdate({ _id: id}, { $set: updateCarDto })
    return updatedCar
  }

  async remove(id: string) {
    const deletedCar = await this.carModel.findByIdAndDelete(id);
    if (!deletedCar) {
      throw new BadRequestException(`Car with id ${id} not found`);
    }
    return deletedCar
      .populate({
        path: 'parkingSpace',
        populate: {
          path: 'smartPlug parkingSensor',
      }})
  }

  async getCarByParkingSpaceId(parkingSpaceId: number): Promise<Car> {
    const parkingSpace = await this.parkingSpaceModel.findOne({ alias: parkingSpaceId });
    return this.carModel
      .findOne({ parkingSpace })
      .populate({
        path: 'parkingSpace',
        populate: {
          path: 'smartPlug parkingSensor',
      }})
  }

  async getCarByLicensePlate(licensePlate: string): Promise<Car> {
    return this.carModel
      .findOne({ licensePlate: licensePlate })
      .populate({
        path: 'parkingSpace',
        populate: {
          path: 'smartPlug parkingSensor',
      }});
  }

  async getParkingSpaceAliasByParkingSensor(macAddress: string): Promise<number> {
      const parkingSensor = await this.parkingSensorModel.findOne({ macAddress: macAddress });
      const parkingSpace = await this.parkingSpaceModel.findOne({ parkingSensor: parkingSensor });
      return parkingSpace.alias;
  }

  async getParkingSpaceAliasByPlug(macAddress: string): Promise<number> {
    const smartPlug = await this.smartPlugModel.findOne({ macAddress: macAddress });
    const parkingSpace = await this.parkingSpaceModel.findOne({ smartPlug: smartPlug });
    return parkingSpace.alias;
  }

  async getPlugMacAddressByParkingSpaceId(parkingSpaceId: number): Promise<string> {
    const parkingSpace = await this.parkingSpaceModel.findOne({ alias: parkingSpaceId });
    const smartPlug = await this.smartPlugModel.findOne({ _id: parkingSpace.smartPlug });
    return smartPlug.macAddress;
  }

  async removeReasoningFields() {
    await this.carModel.updateMany({}, {
      $unset: {
        isParked: "",
        parkedSince: "",
        chargingEnabled: "",
        chargingEnabledSince: "",
        charging: "",
        chargingSince: "",
        chargingPower: "",
        chargingPlan: "",
        departureTime: "",
        carNotPluggedIn: "",
        carUnpluggedEarly: "",
        emergencyCharging: "",
        calendarEntries: "",
        planGenerating: "",
        startSoC: ""
      }
    });
  }
}
