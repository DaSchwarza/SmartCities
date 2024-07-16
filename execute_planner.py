import json
import os
import subprocess
import paho.mqtt.client as mqtt
from datetime import datetime

MQTT_BROKER = "167.172.166.109"
MQTT_PORT = 1883
MQTT_USER = "local"
MQTT_PASSWORD = "Stuttgart"
MQTT_TOPIC = "/standardized/plan/created"

def extract_prices_from_json(data):
    prices = {}
    for entry in data:
        timestamp = datetime.fromisoformat(entry["timestamp"].replace("Z", "+00:00"))
        time_slot = timestamp.strftime('%H%M')
        prices[time_slot] = {
            "price": entry["price"],
            "timestamp": entry["timestamp"]
        }
    return prices


def extract_cars_from_json(data):
    car_data = data["car"]
    cars = [
        {
            "id": car_data["car_id"],
            "required_time": car_data["required_cycles"],
            "deadline": car_data["deadline"],
            "parkingSpace": 1  # Annahme eines einzelnen Parkplatzes, da die Daten ihn nicht bereitstellen
        }
    ]
    return cars


def update_pddl_files(prices, cars):
    domain_template = """
    (define (domain charging)
  (:types car parkingspot time)

  (:predicates 
    (charging ?c - car ?s - parkingspot ?t - time)
    (time-slot ?t - time))  ; Definition des Zeitslot-Prädikats

  (:action start-charging
    :parameters (?c - car ?s - parkingspot ?t - time)
    :precondition (and (time-slot ?t))  ; Verwendung des Prädikats
    :effect (charging ?c ?s ?t))
    )
    """

    problem_template = """
    (define (problem charging-problem)
      (:domain charging)
      (:objects 
        {car_objects} - car
        {parkingspot_objects} - parkingspot
        {time_objects} - time)
      
      (:init 
        {time_slots_init}  ; Initialisierung der Zeitslots
        )
      
      (:goal (and 
        {charging_goals}))
    )
    """

    # Find the cheapest times
    sorted_times = sorted(prices.items(), key=lambda item: item[1]["price"])
    
    # Prepare car and parkingspot objects
    car_objects = " ".join(car['id'] for car in cars)
    parkingspot_objects = " ".join(f"parkingspot{car['parkingSpace']}" for car in cars)

    # Generate time objects and initialize time slots dynamically based on deadlines
    time_slots = set()
    charging_goals = []
    for car in cars:
        car_id = car['id']
        parkingspot_id = f"parkingspot{car['parkingSpace']}"
        required_times = car['required_time']
        deadline = car['deadline']
        available_time_slots = get_time_slots_until(deadline)
        time_slots.update(available_time_slots)
        for time_index in range(required_times):
            if time_index < len(sorted_times):
                time_slot = sorted_times[time_index][0]
                if time_slot in available_time_slots:
                    charging_goals.append(f"(charging {car_id} {parkingspot_id} t{time_slot})")

    time_objects = " ".join(f"t{slot}" for slot in time_slots)
    time_slots_init = "\n        ".join(f"(time-slot t{slot})" for slot in time_slots)

    domain_path = "C:\\Users\\I518184\\SmartCities\\domain.pddl"
    problem_path = "C:\\Users\\I518184\\SmartCities\\problem.pddl"

    with open(domain_path, "w") as domain_file:
        domain_file.write(domain_template)

    with open(problem_path, "w") as problem_file:
        problem_file.write(problem_template.format(
            car_objects=car_objects,
            parkingspot_objects=parkingspot_objects,
            time_objects=time_objects,
            time_slots_init=time_slots_init,
            charging_goals="\n        ".join(charging_goals)
        ))

def get_time_slots_until(deadline):
    deadline_time = datetime.fromisoformat(deadline)
    return [f"{hour:02}{minute:02}"
            for hour in range(24) for minute in range(0, 60, 5)
            if datetime.strptime(f"{hour:02}:{minute:02}", "%H:%M").replace(tzinfo=deadline_time.tzinfo) <= deadline_time]

def run_planner(domain_file, problem_file, prices):
    planner_path = 'C:\\Planner\\downward-main\\downward-main\\fast-downward.py'
    
    command = [
        'python', planner_path,
        '--alias', 'seq-sat-lama-2011',
        domain_file, problem_file
    ]
    
    result = subprocess.run(command, capture_output=True, text=True)
    if result.returncode == 0:
        plan = parse_plan(result.stdout)
        save_plan_to_file(plan, "sas_plan")
        publish_plan_to_mqtt(plan, prices)
    else:

        # Save stderr to a file for detailed error analysis
        with open("planning_error.log", "w") as error_log:
            error_log.write(result.stderr)

        # Save stdout to a file for detailed output analysis
        with open("planning_output.log", "w") as output_log:
            output_log.write(result.stdout)

def parse_plan(plan_str):
    plan = []
    for line in plan_str.strip().split("\n"):
        parts = line.split()
        if len(parts) >= 4:
            action = parts[0]
            car = parts[1]
            parking_space = parts[2]
            time = parts[3]
            if parking_space.startswith("parkingspot"):
                plan.append({
                    "action": action,
                    "car": car,
                    "parkingSpace": parking_space,
                    "time": time
                })
    return plan

def transform_plan_to_json(parsed_plan, prices):
    transformed_plan = []
    parking_spaces = {}

    # Mapping time slot strings to actual datetimes
    time_slot_to_datetime = {slot: datetime.fromisoformat(entry["timestamp"]) for slot, entry in prices.items()}

    for entry in parsed_plan:
        parking_space = entry["parkingSpace"]
        if parking_space.startswith("parkingspot"):
            if parking_space not in parking_spaces:
                parking_spaces[parking_space] = {
                    "parkingSpace": int(parking_space.replace("parkingspot", "")),
                    "actions": []
                }
            # Use the correct datetime for the action time
            time_slot = entry["time"].replace('t', '')
            if time_slot in time_slot_to_datetime:
                action_time = time_slot_to_datetime[time_slot].isoformat()
                parking_spaces[parking_space]["actions"].append({
                    "action": entry["action"],
                    "car": entry["car"],
                    "time": action_time
                })

    for space in parking_spaces.values():
        transformed_plan.append(space)

    return transformed_plan

def save_plan_to_file(plan, filename):
    with open(filename, 'w') as f:
        for step in plan:
            f.write(f"({step['action']} {step['car']} {step['parkingSpace']} {step['time']})\n")

def publish_plan_to_mqtt(plan, prices):
    transformed_plan = transform_plan_to_json(plan, prices)
    client = mqtt.Client()
    client.username_pw_set(MQTT_USER, MQTT_PASSWORD)
    client.connect(MQTT_BROKER, MQTT_PORT, 60)
    client.loop_start()
    client.publish(MQTT_TOPIC, json.dumps(transformed_plan), qos=1)
    client.loop_stop()
    client.disconnect()

def start_execution(data):
    prices = extract_prices_from_json(data["prices"])
    cars = extract_cars_from_json(data)
    if prices:
        update_pddl_files(prices, cars)
        domain_file = 'C:\\Users\\I518184\\SmartCities\\domain.pddl'
        problem_file = 'C:\\Users\\I518184\\SmartCities\\problem.pddl'
        run_planner(domain_file, problem_file, prices)

def on_connect(client, userdata, flags, rc):
    print(f"Connected to MQTT broker with result code {rc}")
    client.subscribe("/standardized/plan/create")

def on_message(client, userdata, msg):
    print(f"Message received: {msg.topic} {msg.payload}")
    if msg.topic == "/standardized/plan/create":
        data = json.loads(msg.payload.decode('utf-8'))["data"]
        start_execution(data)


if __name__ == "__main__":
    client = mqtt.Client()
    client.username_pw_set(MQTT_USER, MQTT_PASSWORD)
    client.on_connect = on_connect
    client.on_message = on_message

    client.connect(MQTT_BROKER, MQTT_PORT, 60)
    client.loop_forever()
