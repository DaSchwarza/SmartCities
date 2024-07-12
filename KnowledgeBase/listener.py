import os

import json
from datetime import datetime
from pymongo import MongoClient
import paho.mqtt.client as mqtt
from dotenv import load_dotenv

load_dotenv()

mongo_uri = os.getenv("MONGO_URI")
database_name = os.getenv("KNOWLEDGE_DATABASE")
collection_name = os.getenv("RAW_DATA_COLLECTION")

# MongoDB setup
client = MongoClient(mongo_uri, 27017)  # Update with your MongoDB server info
db = client[database_name]
collection = db[collection_name]

# MQTT setup
mqtt_broker = os.getenv("MQTT_BROKER")
mqtt_port = int(os.getenv('MQTT_PORT'))
mqtt_user = os.getenv("MQTT_USER")
mqtt_password = os.getenv("MQTT_PASSWORD")

print(mqtt_broker, mqtt_port, mqtt_user, mqtt_password)


# MQTT callback functions
def on_connect(client, userdata, flags, rc):
    print(f"Connected with result code {rc}")
    client.subscribe("/parking/#")
    client.subscribe("plugwise2py/state/power/#")
    client.subscribe("plugwise2py/cmd/switch/#")


def on_message(client, userdata, msg):
    topic = msg.topic
    payload = json.loads(msg.payload.decode())

    if '/parking/' in topic:
        mac_address = topic.split('/')[-1]
        data = {
            "sensor_type": "parking",
            "variable": "occupation",
            "mac_adress": mac_address,
            "occupied": payload.get('occupied', False)
        }
        collection.insert_one(data)

    elif 'plugwise2py/state/power/' in topic:
        mac_address = topic.split('/')[-1]
        data = {
            "sensor_type": "smart_plug",
            "variable": "power_reading",
            "mac_adress": mac_address,
            "timestamp": datetime.fromtimestamp(payload['ts']),
            "power": payload.get('power', 0.00)
        }
        collection.insert_one(data)

    elif 'plugwise2py/cmd/switch/' in topic:
        mac_address = topic.split('/')[-1]
        enabled_status = True if payload.get('val', 'off') == 'on' else False
        data = {
            "sensor_type": "smart_plug",
            "variable": "status",
            "mac_adress": mac_address,
            "enabled": enabled_status
        }
        collection.insert_one(data)


# MQTT Client
client = mqtt.Client()
client.username_pw_set(mqtt_user, mqtt_password)
client.on_connect = on_connect
client.on_message = on_message

client.connect(mqtt_broker, mqtt_port, 60)

# Blocking call - processes MQTT messages and runs forever
client.loop_forever()
