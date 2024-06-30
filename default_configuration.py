import os
import pymongo
from dotenv import load_dotenv


def initialize_configurations():
    # Load environment variables
    load_dotenv()

    # Connect to MongoDB using environment variables
    mongo_uri = os.getenv('MONGO_URI')
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
        {"variable": "battery_capacity", "value": 80}
    ]

    # Update or insert default configurations
    for config in default_configs:
        config_collection.update_one(
            {"variable": config["variable"]},  # Query for matching document
            {"$set": {"value": config["value"]}},  # Values to update
            upsert=True  # Insert if not exists
        )
        print(f"Configuration for {config['variable']} set to {config['value']}.")


def main():
    initialize_configurations()


if __name__ == "__main__":
    main()
