import os
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
    collection_name = os.getenv('DEVICE_COLLECTION')
    client = pymongo.MongoClient(mongo_uri)
    db = client[db_name]
    device_collection = db[collection_name]

    # Default Devices
    # Insert Sensors
    sensors = [
        {"id": 1, "mac_address": "00:11:22:33:44:55", "type": "parking_sensor"},
        {"id": 2, "mac_address": "66:77:88:99:AA:BB", "type": "parking_sensor"}
    ]

    # Insert Plugs
    plugs = [
        {"id": 1, "mac_address": "00:11:22:33:44:56", "type": "smart_plug"},
        {"id": 2, "mac_address": "66:77:88:99:AA:BC", "type": "smart_plug"}
    ]

    # Insert Parking Spaces
    parking_spaces = [
        {"id": 1, "sensor_id": 1, "plug_id": 1, "type": "parking_space"},
        {"id": 2, "sensor_id": 2, "plug_id": 2, "type": "parking_space"}
    ]

    # Insert Cars
    cars = [
        {"license_plate": "ETRON1", "manufacturer": "Audi", "model": "Etron", "battery_capacity": 95,
         "parking_space_id": 1, "type": "car"},
        {"license_plate": "FUNCY1", "manufacturer": "Ora", "model": "Funcycat", "battery_capacity": 47,
         "parking_space_id": 2, "type": "car"}
    ]

    # Insert all documents into the collection
    device_collection.insert_many(sensors + plugs + parking_spaces + cars)
    print("Entities initialized successfully in MongoDB.")


def main():
    initialize_configurations()
    initialize_entities()


if __name__ == "__main__":
    main()
