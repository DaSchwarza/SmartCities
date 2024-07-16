import paho.mqtt.client as mqtt
import time
from datetime import datetime, timedelta, timezone
import json

MQTT_BROKER = "167.172.166.109"
MQTT_PORT = 1883
MQTT_USER = "local"
MQTT_PASSWORD = "Stuttgart"
MQTT_TOPIC = "/standardized/plan/created"

plan = []  # Variable to store the plan

def on_connect(client, userdata, flags, rc):
    print(f"Connected to MQTT broker with result code {rc}")
    client.subscribe(MQTT_TOPIC)

def on_message(client, userdata, msg):
    global plan
    print(f"Message received: {msg.topic} {msg.payload}")
    if msg.topic == MQTT_TOPIC:
        plan = json.loads(msg.payload)
        print(f"Plan updated: {plan}")


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

    is_charging = {}
    last_action_time = {}

    print("Starting plan execution")
    while True:
        current_time = datetime.now(timezone.utc).astimezone().replace(second=0, microsecond=0)
        current_time_iso = current_time.isoformat()
        print(f"Current ISO time: {current_time_iso}")
        for parking_space_entry in plan:
            parking_space = parking_space_entry["parkingSpace"]
            for action in parking_space_entry["actions"]:
                try:
                    action_time_iso = action["time"]
                    action_time = datetime.fromisoformat(action_time_iso).replace(second=0, microsecond=0)
                    print(f"Checking action {action['action']} at {action_time_iso} for parking space {parking_space}")
                    
                    if action_time == current_time:  # Exact match on minute precision
                        print(f"Action {action['action']} matches current time {current_time_iso}")
                        
                        if action["action"] == "start-charging":
                            # Check if this is a continuation of a previous charging slot
                            if parking_space in last_action_time:
                                last_time = last_action_time[parking_space]
                                if action_time - last_time <= timedelta(minutes=5):
                                    print(f"Continuing charging for parking space {parking_space}")
                                    last_action_time[parking_space] = action_time
                                    continue  # Skip sending start command as it's a continuation

                            send_mqtt_command(client, parking_space, True)
                            is_charging[parking_space] = True
                            last_action_time[parking_space] = action_time

                            # Schedule stop command 5 minutes after the last start-charging action
                            stop_time = (action_time + timedelta(minutes=5)).replace(second=0, microsecond=0).isoformat()
                            parking_space_entry["actions"].append({
                                "action": "stop-charging",
                                "car": action["car"],
                                "parkingSpace": action["parkingSpace"],
                                "time": stop_time
                            })
                            print(f"Scheduled stop-charging at {stop_time} for parking space {parking_space}")
                        
                        elif action["action"] == "stop-charging":
                            # Check if the next action is within the next 5 minutes
                            if parking_space in last_action_time:
                                next_action_time = last_action_time[parking_space] + timedelta(minutes=5)
                                if next_action_time == action_time:
                                    print(f"Skipping stop-charging as next slot continues for parking space {parking_space}")
                                    continue  # Skip stopping as the next slot is a continuation
                            
                            if is_charging.get(parking_space, False):
                                send_mqtt_command(client, parking_space, False)
                                is_charging[parking_space] = False
                                print("Charging stopped")
                except KeyError as e:
                    print(f"KeyError: {e}. Action: {action}")
        time.sleep(20)  # Wait 20 seconds before checking the plan again

if __name__ == "__main__":
    execute_plan()



