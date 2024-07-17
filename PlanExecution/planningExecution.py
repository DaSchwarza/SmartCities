import paho.mqtt.client as mqtt
import time
from datetime import datetime, timedelta, timezone
import json

MQTT_BROKER = "167.172.166.109"
MQTT_PORT = 1883
MQTT_USER = "local"
MQTT_PASSWORD = "Stuttgart"
MQTT_TOPIC = "/standardized/plan/created"

plan = [] 
is_charging = {}

def on_connect(client, userdata, flags, rc):
    print(f"Connected to MQTT broker with result code {rc}")
    client.subscribe(MQTT_TOPIC)

def on_message(client, userdata, msg):
    global plan
    global is_charging
    print(f"Message received: {msg.topic} {msg.payload}")
    if msg.topic == MQTT_TOPIC:
        plan = json.loads(msg.payload)
        print(f"Plan updated: {plan}")
        for car_plan in plan:
            parking_space = car_plan.get("parkingSpace")
            is_charging[parking_space] = False

def send_mqtt_command(client, parking_space_id, command):
    message = {
        "enabled": command
    }
    topic = f"/standardized/execute/{parking_space_id}"
    client.publish(topic, json.dumps(message))
    print(f"Sent MQTT message: {json.dumps(message)} to topic: {topic}")

def execute_plan():
    client = mqtt.Client()
    client.username_pw_set(MQTT_USER, MQTT_PASSWORD)
    client.on_connect = on_connect
    client.on_message = on_message

    client.connect(MQTT_BROKER, MQTT_PORT, 60)
    client.loop_start()

    global is_charging
    last_action_time = {}

    print("Starting plan execution")
    while True:
        current_time = datetime.now(timezone.utc).replace(second=0, microsecond=0)
        current_time_iso = current_time.isoformat()
        print(f"Current UTC time: {current_time_iso}")
        for parking_space_entry in plan:
            parking_space = parking_space_entry["parkingSpace"]
            for action in parking_space_entry["actions"]:
                try:
                    start_time_iso = action["start_time"]
                    end_time_iso = action["end_time"]
                    start_time = datetime.fromisoformat(start_time_iso).replace(second=0, microsecond=0)
                    end_time = datetime.fromisoformat(end_time_iso).replace(second=0, microsecond=0)
                    print(f"Checking action {action['action']} from {start_time_iso} to {end_time_iso} for parking space {parking_space}")
                    
                    if start_time <= current_time < end_time:  # Current time is within the action period
                        print(f"Action {action['action']} is active at {current_time_iso}")
                        
                        if action["action"] == "start-charging":
                            # Check if charging is already active for this parking space
                            print(f"{current_time}: is charging {is_charging.get(parking_space)}")
                            if not is_charging.get(parking_space, False):
                                send_mqtt_command(client, parking_space, True)
                                is_charging[parking_space] = True
                                last_action_time[parking_space] = start_time
                                print(f"Started charging for parking space {parking_space}")
                        
                        elif action["action"] == "stop-charging":
                            # Check if charging is currently active for this parking space
                            if is_charging.get(parking_space, False):
                                send_mqtt_command(client, parking_space, False)
                                is_charging[parking_space] = False
                                print(f"Stopped charging for parking space {parking_space}")
                except KeyError as e:
                    print(f"KeyError: {e}. Action: {action}")
        time.sleep(10)  # Wait 20 seconds before checking the plan again

if __name__ == "__main__":
    execute_plan()
