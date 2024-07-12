import os

import requests
import pymongo
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()


def fetch_office_plz():
    # Connect to MongoDB to retrieve configuration
    mongo_uri = os.getenv("MONGO_URI")
    database_name = os.getenv("CONFIGURATION_DATABASE")
    collection_name = os.getenv("CONFIGURATION_COLLECTION")
    client = pymongo.MongoClient(mongo_uri)
    db = client[database_name]
    config_collection = db[collection_name]

    # Fetch the office_plz configuration
    config_data = config_collection.find_one({"variable": "office_plz"})
    if not config_data:
        print("Error retrieving office_plz")
        return None
    return config_data.get("value", "")


def fetch_prices_from_api(office_plz):
    # API URL for fetching data
    api_url = f"https://tibber.com/de/api/lookup/price-overview?postalCode={office_plz}"
    response = requests.get(api_url)

    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to fetch data: {response.status_code} - {response.text}")
        return None


def save_prices_to_mongodb(data):
    # Connect to MongoDB
    mongo_uri = os.getenv("MONGO_URI")
    database_name = os.getenv("PRICES_DATABASE")
    collection_name = os.getenv("PRICES_COLLECTION")
    client = pymongo.MongoClient(mongo_uri)
    db = client[database_name]
    collection = db[collection_name]

    today_date = datetime.now().strftime("%Y-%m-%d")

    # Process hourly prices
    print("{")
    for hour_data in data['energy']['todayHours']:
        hour = hour_data['hour']
        price_incl_vat = hour_data['priceIncludingVat']

        # Generate datetime for each minute within this hour
        for minute in range(0, 60, 5):
            timestamp = datetime.strptime(f"{today_date} {hour}:{minute:02}", "%Y-%m-%d %H:%M")
            price_document = {
                "$set": {"price": price_incl_vat}
            }
            collection.update_one({ "timestamp": timestamp}, price_document, upsert=True)
            print(f'    "timestamp": {timestamp}, "price": {price_incl_vat:.4f},')
    print("}")
    print(f"Successfully retrieved prices for {today_date}")


def main():
    # Fetch office_plz from configuration
    office_plz = fetch_office_plz()
    if not office_plz:
        print("office_plz configuration is missing, skipping ...")
        return None
    # Fetch prices from API with office_plz
    price_data = fetch_prices_from_api(office_plz)
    if not price_data:
        print("No data fetched, skipping ...")
        return None
    # Save fetched prices to MongoDB
    save_prices_to_mongodb(price_data)


if __name__ == "__main__":
    main()
