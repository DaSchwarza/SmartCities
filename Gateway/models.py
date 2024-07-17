import os

from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

mongo_uri = os.getenv("MONGO_URI")
database_name = os.getenv("KNOWLEDGE_DATABASE")
collection_name = os.getenv("DEVICE_COLLECTION")

# MongoDB setup
client = MongoClient(mongo_uri, 27017)  # Adjust as needed
db = client[database_name]
collection = db[collection_name]


class ParkingSensor:
    def __init__(self, id, mac_address):
        self.id = id
        self.mac_address = mac_address
        self.reading = None
        self.occupation = None

    def to_dict(self):
        return {"id": self.id, "mac_address": self.mac_address, "reading": self.reading, "occupation": self.occupation}


class SmartPlug:
    def __init__(self, id, mac_address):
        self.id = id
        self.mac_address = mac_address
        self.power = None
        self.enabled = None

    def to_dict(self):
        return {"id": self.id, "mac_address": self.mac_address, "power": self.power, "enabled": self.enabled}


class ParkingSpace:
    def __init__(self, id, sensor_id, plug_id, sensors, plugs):
        self.id = id
        self.sensor = sensors.get(sensor_id)
        self.plug = plugs.get(plug_id)

    def to_dict(self):
        return {"id": self.id, "sensor": self.sensor.to_dict() if self.sensor else None,
                "plug": self.plug.to_dict() if self.plug else None}


class Car:
    def __init__(self, license_plate, manufacturer, model, battery_capacity, parking_space_id, parking_spaces):
        self.license_plate = license_plate
        self.manufacturer = manufacturer
        self.model = model
        self.battery_capacity = battery_capacity
        self.parking_space = parking_spaces.get(parking_space_id)
        self.away = False
        self.charging_enabled = None
        self.charging_power = None
        self.charging_plan = None

    def to_dict(self):
        return {
            "license_plate": self.license_plate,
            "manufacturer": self.manufacturer,
            "model": self.model,
            "battery_capacity": self.battery_capacity,
            "parking_space": self.parking_space.to_dict() if self.parking_space else None
        }


def load_entities():
    sensors = {
        doc['id']: ParkingSensor(doc['id'], doc['mac_address'])
        for doc in collection.find({"type": "parking_sensor"})
    }
    plugs = {
        doc['id']: SmartPlug(doc['id'], doc['mac_address'])
        for doc in collection.find({"type": "smart_plug"})
    }
    parking_spaces = {
        doc['id']: ParkingSpace(doc['id'], doc['sensor_id'], doc['plug_id'], sensors, plugs)
        for doc in collection.find({"type": "parking_space"})
    }
    cars = {
        doc['license_plate']: Car(doc['license_plate'], doc['manufacturer'], doc['model'], doc['battery_capacity'],
                                  doc['parking_space_id'], parking_spaces)
        for doc in collection.find({"type": "car"})
    }

    return sensors, plugs, parking_spaces, cars
