import os

import requests
import pymongo
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()


def fetch_prices_from_api():
    # Get today's date and time for 'start', and tomorrow's date and a specified end time for 'end'
    now = datetime.utcnow()
    start_date = now.strftime('%Y-%m-%dT02:00Z')  # Assuming prices start from 02:00 UTC of the current day
    end_date = (now + timedelta(days=1)).strftime(
        '%Y-%m-%dT21:00Z')  # Assuming you want to end at 20:00 UTC of the next day

    # Construct the API URL with dynamic start and end dates
    api_url = f"https://api.energy-charts.info/price?bzn=DE-LU&start={start_date}&end={end_date}"
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

    unix_seconds = data['unix_seconds']
    prices = data['price']
    # Process hourly prices
    for unix_time, price in zip(unix_seconds, prices):
        base_time = datetime.utcfromtimestamp(unix_time)
        for minute in range(0, 60, 5):  # Generating entries for every 5 minutes
            timestamp = base_time + timedelta(minutes=minute)
            # convert price to EUR / KWH and add flat grid fees
            kwh_price = price / 1000 + 0.2
            formatted_timestamp = timestamp.strftime('%Y-%m-%dT%H:%M:%S.000Z')
            price_document = {
                "timestamp":formatted_timestamp,
                "price": kwh_price
            }
            collection.insert_one(price_document)
    print(f"Successfully retrieved prices")


def main():
    # Fetch prices from API
    price_data = fetch_prices_from_api()
    if not price_data:
        print("No data fetched, skipping ...")
        return None
    # Save fetched prices to MongoDB
    save_prices_to_mongodb(price_data)


if __name__ == "__main__":
    main()
