import os
from bson import ObjectId
import pymongo
from dotenv import load_dotenv

mongo_uri = os.getenv('MONGO_URI')


def initialize_configurations():
    # Load environment variables
    load_dotenv()

    # Connect to MongoDB using environment variables
    db_name = os.getenv('CONFIGURATION_DATABASE')
    collection_name = os.getenv('CONFIGURATION_COLLECTION')
    client = pymongo.MongoClient(mongo_uri)
    db = client[db_name]
    config_collection = db[collection_name]

    # List of configurations to be set or updated
    default_configs = [
        {"variable": "office_plz", "value": "70173"},
        {"variable": "start_soc", "value": 20},
        {"variable": "target_soc", "value": 80},
    ]

    # Update or insert default configurations
    for config in default_configs:
        config_collection.update_one(
            {"variable": config["variable"]},  # Query for matching document
            {"$set": {"value": config["value"]}},  # Values to update
            upsert=True  # Insert if not exists
        )
        print(f"Configuration for {config['variable']} set to {config['value']}.")


def initialize_entities():
    # Connect to MongoDB using environment variables
    db_name = os.getenv('KNOWLEDGE_DATABASE')
    client = pymongo.MongoClient(mongo_uri)
    db = client[db_name]

    # Default Devices
    # Insert Sensors
    sensors = [
        {"_id": ObjectId("66910af0cd4ecc530d0c9bc8"), "alias": 1, "macAddress": "bef54ca19801", "type": "parking_sensor"},
        {"_id": ObjectId("66910b021e707ca140dbaecf"), "alias": 2, "macAddress": "481930d7ba90", "type": "parking_sensor"}
    ]
    sensorCollection = db["parkingsensors"]
    sensorCollection.delete_many({})
    sensorCollection.insert_many(sensors)

    # Insert Plugs
    plugs = [
        {"_id": ObjectId("66910b1fa74174b0d5475cd2"), "alias": 1, "macAddress": "000D6F0005692B55"},
        {"_id": ObjectId("66910b2657f3885d66106594"), "alias": 2, "macAddress": "000D6F0004B1E6C4"}
    ]
    plugCollection = db["smartplugs"]
    plugCollection.delete_many({})
    plugCollection.insert_many(plugs)

    # Insert Parking Spaces
    parking_spaces = [
        {"_id": ObjectId("66910b3ad9534f539c120903"), "alias": 1, "parkingSensor": ObjectId("66910af0cd4ecc530d0c9bc8"), "smartPlug": ObjectId("66910b1fa74174b0d5475cd2")},
        {"_id": ObjectId("66910b4184d0ade72f24d174"), "alias": 2, "parkingSensor": ObjectId("66910b021e707ca140dbaecf"), "smartPlug": ObjectId("66910b2657f3885d66106594")}
    ]
    parkingSpaceCollection = db["parkingspaces"]
    parkingSpaceCollection.delete_many({})
    parkingSpaceCollection.insert_many(parking_spaces)

    # Insert Cars
    cars = [
        {"licensePlate": "F-UN-404", "manufacturer": "Audi", "model": "Etron", "batteryCapacity": 95,
         "parkingSpace": ObjectId("66910b3ad9534f539c120903")},
        {"licensePlate": "BI-ER-200", "manufacturer": "Ora", "model": "Funcycat", "batteryCapacity": 47,
         "parkingSpace": ObjectId("66910b4184d0ade72f24d174")}
    ]
    carCollection = db["cars"]
    carCollection.delete_many({})
    carCollection.insert_many(cars)

    print("Entities initialized successfully in MongoDB.")


def main():
    initialize_configurations()
    initialize_entities()


if __name__ == "__main__":
    main()
