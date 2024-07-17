export class CarPlanDto {
    parkingSpace: number;
    actions: CarActionDto[];
}

export class CarActionDto {
    action: string;
    start_time: string;
    end_time: string;
    spot: string;
}