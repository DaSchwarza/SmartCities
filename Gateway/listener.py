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

# MQTT callback functions
def on_connect(client, userdata, flags, rc):
    print(f"Connected with result code {rc}")
    client.subscribe("/parking/#")
    client.subscribe("plugwise2py/state/power/#")
    client.subscribe("plugwise2py/cmd/switch/#")
    client.subscribe("/standardized/execute/mac/#")


def on_message(client, userdata, msg):
    topic = msg.topic
    payload = json.loads(msg.payload.decode())

    if '/parking/' in topic:
        mac_address = topic.split('/')[-1]
        time = datetime.now().isoformat()
        data = {
            "sensor_type": "parking",
            "variable": "occupation",
            "mac_adress": mac_address,
            "timestamp": time,
            "occupied": payload.get('occupied', False),
            "distance_cm": payload.get('distance_cm', 0),
        }
        collection.insert_one(data)
        # Publish in standardized format
        publish(f'/standardized/parking/{mac_address}/occupation', json.dumps(data, default=str))

    elif 'plugwise2py/state/power/' in topic:
        mac_address = topic.split('/')[-1]
        timestamp = payload.get("ts")
        time = datetime.fromtimestamp(timestamp).isoformat()
        # simulate KW consumption
        power = payload.get('power') * 1000
        data = {
            "sensor_type": "smart_plug",
            "variable": "power_reading",
            "mac_adress": mac_address,
            "timestamp": time,
            "power": power
        }
        collection.insert_one(data)
        # Publish in standardized format
        publish(f'/standardized/parking/{mac_address}/power', json.dumps(data, default=str))

    elif 'plugwise2py/cmd/switch/' in topic:
        mac_address = topic.split('/')[-1]
        time = datetime.now().isoformat()
        enabled_status = True if payload.get('val', 'off') == 'on' else False
        data = {
            "sensor_type": "smart_plug",
            "variable": "status",
            "mac_adress": mac_address,
            "timestamp": time,
            "enabled": enabled_status
        }
        collection.insert_one(data)
        # Publish in standardized format
        publish(f'/standardized/parking/{mac_address}/charging/status', json.dumps(data, default=str))

    elif '/standardized/execute/mac' in topic:
        mac_address = topic.split('/')[-1]
        data = payload.get('data')
        time = datetime.now().isoformat()
        enabled = data.get('enabled', False)
        data = {
            "actor_type": "smart_plug",
            "variable": "status",
            "mac_adress": mac_address,
            "timestamp": time,
            "enabled": enabled
        }
        collection.insert_one(data)
        payload = {
            "mac": "",
            "cmd": "switch",
            "val": "on" if enabled else "off"
        }
        publish(f'plugwise2py/cmd/switch/{mac_address}', json.dumps(payload))
def publish(topic, payload):
    client.publish(topic, payload)


# MQTT Client
client = mqtt.Client()
client.username_pw_set(mqtt_user, mqtt_password)
client.on_connect = on_connect
client.on_message = on_message

client.connect(mqtt_broker, mqtt_port, 60)

# Blocking call - processes MQTT messages and runs forever
client.loop_forever()
