export class ChargingPlanElement {
  from: Date;
  to: Date;

  constructor(from: Date, to: Date) {
    this.from = from;
    this.to = to;
  }
}

export class ChargingPlan {
  planElements: ChargingPlanElement[];
  createdAt: Date;

  constructor(planElements: ChargingPlanElement[], createdAt: Date) {
    this.planElements = planElements;
    this.createdAt = createdAt;
  }
}

export class TimelineEntry {
  type: 'charging' | 'inUse' | 'idle';
  from: Date;
  to: Date;

  constructor(type: 'charging' | 'inUse' | 'idle', from: Date, to: Date) {
    this.type = type;
    this.from = from;
    this.to = to;
  }
}

export class Car {
  _id: string;
  licensePlate: string;
  manufacturer: string;
  model: string;
  batteryCapacity: number;
  isParked?: boolean;
  parkedSince?: Date;
  chargingEnabled?: boolean;
  chargingEnabledSince?: Date;
  charging?: boolean;
  chargingSince?: Date;
  chargingPower?: number;
  chargingPlan?: ChargingPlan;
  calendarEntries?: ChargingPlanElement[];
  timelineEntries?: TimelineEntry[];
  departureTime?: Date;
  carNotPluggedIn?: boolean;
  carUnpluggedEarly?: boolean;
  startSoC?: number;
  emergencyCharging?: boolean;
  planGenerating?: boolean;
  calendarLink?: string;

  constructor(_id: string, licensePlate: string, manufacturer: string, model: string, batteryCapacity: number, calendarLink: string, isParked?: boolean, parkedSince?: Date, chargingEnabled?: boolean, chargingEnabledSince?: Date, charging?: boolean, chargingSince?: Date, chargingPower?: number, chargingPlan?: ChargingPlan, calendarEntries?: ChargingPlanElement[], timelineEntries?: TimelineEntry[], departureTime?: Date, carNotPluggedIn?: boolean, carUnpluggedEarly?: boolean, startSoC?: number, emergencyCharging?: boolean, planGenerating?: boolean) {
    this._id = _id;
    this.licensePlate = licensePlate;
    this.manufacturer = manufacturer;
    this.model = model;
    this.batteryCapacity = batteryCapacity;
    this.calendarLink = calendarLink;
    if (isParked) this.isParked = isParked;
    if (parkedSince) this.parkedSince = parkedSince;
    if (chargingEnabled) this.chargingEnabled = chargingEnabled;
    if (chargingEnabledSince) this.chargingEnabledSince = chargingEnabledSince;
    if (charging) this.charging = charging;
    if (chargingSince) this.chargingSince = chargingSince;
    if (chargingPower) this.chargingPower = chargingPower;
    if (chargingPlan) this.chargingPlan = chargingPlan;
    if (calendarEntries) this.calendarEntries = calendarEntries;
    if (timelineEntries) this.timelineEntries = timelineEntries;
    if (departureTime) this.departureTime = departureTime;
    if (carNotPluggedIn) this.carNotPluggedIn = carNotPluggedIn;
    if (carUnpluggedEarly) this.carUnpluggedEarly = carUnpluggedEarly;
    if (startSoC) this.startSoC = startSoC;
    if (emergencyCharging) this.emergencyCharging = emergencyCharging;
    if (planGenerating) this.planGenerating = planGenerating;
  }
}