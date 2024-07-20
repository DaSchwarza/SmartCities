import json
import os
import subprocess
from time import timezone
import paho.mqtt.client as mqtt
from datetime import datetime, timedelta, timezone


MQTT_BROKER = "167.172.166.109"
MQTT_PORT = 1883
MQTT_USER = "local"
MQTT_PASSWORD = "Stuttgart"
MQTT_TOPIC = "/standardized/plan/created"
DOMAIN_FILE_PATH = "C:\\Users\\I518184\\SmartCities\\DecisionMaking\\domain.pddl"
PROBLEM_FILE_PATH = "C:\\Users\\I518184\\SmartCities\\DecisionMaking\\problem.pddl"


def extract_prices_from_json(data):
    prices = {}
    for entry in data:
        timestamp = datetime.fromisoformat(entry["timestamp"].replace("Z", "+00:00")).strftime('%d%H%M')
        scaled_price = int(entry["price"] * 1000)
        prices[timestamp] = {
            "price": scaled_price,
            "timestamp": entry["timestamp"]
        }
    return prices


def round_to_nearest_5_minutes(dt):
    discard = timedelta(minutes=dt.minute % 5, seconds=dt.second, microseconds=dt.microsecond)
    return dt - discard


def extract_cars_from_json(data):
    car_data = data["car"]
    deadline = datetime.fromisoformat(car_data["deadline"].replace("Z", "+00:00"))
    adjusted_deadline = deadline - timedelta(minutes=5)
    rounded_deadline = round_to_nearest_5_minutes(adjusted_deadline).isoformat()
    cars = [
        {
            "id": car_data["car_id"],
            "required_time": car_data["required_cycles"],
            "deadline": rounded_deadline,
            "parkingSpace": car_data["parkingSpace"]
        }
    ]
    return cars

def update_problem_file(prices, cars):
    problem_template = """
    (define (problem charging-problem)
      (:domain charging)
      (:objects 
        {car_objects} - car
        {parkingspot_objects} - parkingspot
        {time_objects} - time
      )
      
      (:init 
        {time_slots_init}  ; Initialisierung der Zeitslots
        {car_at_init}      ; Initialisierung der Autos an Parkplätzen
        (= (total-cost) 0)
        {time_costs}       ; Kosten für die Zeitslots
      )
      
      (:goal (and 
        {charging_goals}
      ))
      
      (:metric minimize (total-cost))
    )
    """
    
    car_objects = " ".join(car['id'] for car in cars)
    parkingspot_objects = " ".join(f"parkingspot{car['parkingSpace']}" for car in cars)
    
    time_slots = set()
    car_at_init = []
    time_costs = []

    for car in cars:
        car_id = car['id']
        parkingspot_id = f"parkingspot{car['parkingSpace']}"
        deadline = car['deadline']
        available_time_slots = get_time_slots_until(deadline)
        time_slots.update(available_time_slots)
        car_at_init.append(f"(car-at {car_id} {parkingspot_id})")

        for time_slot in available_time_slots:
            if time_slot in prices:
                time_costs.append(f"(= (cost-of t{time_slot}) {prices[time_slot]['price']})")

    time_objects = " ".join(f"t{slot}" for slot in time_slots)
    time_slots_init = "\n        ".join(f"(time-slot t{slot})" for slot in time_slots)
    charging_goals = []
    for car in cars:
        car_id = car['id']
        parkingspot_id = f"parkingspot{car['parkingSpace']}"
        charging_goals.append(f"(exists (?t - time) (charging {car_id} {parkingspot_id} ?t))")

    new_problem_file_content = problem_template.format(
        car_objects=car_objects,
        parkingspot_objects=parkingspot_objects,
        time_objects=time_objects,
        time_slots_init=time_slots_init,
        car_at_init="\n        ".join(car_at_init),
        time_costs="\n        ".join(time_costs),
        charging_goals="\n        ".join(charging_goals)
    )

    if os.path.exists(PROBLEM_FILE_PATH):
        with open(PROBLEM_FILE_PATH, "r") as problem_file:
            current_content = problem_file.read()
        if current_content == new_problem_file_content:
            return

    with open(PROBLEM_FILE_PATH, "w") as problem_file:
        problem_file.write(new_problem_file_content)


def get_time_slots_until(deadline):
    deadline_time = datetime.fromisoformat(deadline)
    slots = []
    current_time = datetime.now(tz=timezone.utc).replace(second=0, microsecond=0)
    
    if current_time.minute % 5 != 0:
        current_time = round_to_nearest_5_minutes(current_time + timedelta(minutes=5))
    
    while current_time <= deadline_time:
        slots.append(current_time.strftime('%d%H%M'))
        current_time += timedelta(minutes=5)
        
        if current_time.time() == datetime.min.time():
            current_time = current_time.replace(second=0, microsecond=0)
    
    return slots


def remove_used_time_slots(prices, used_slots):
    for slot in used_slots:
        timestamp_key = datetime.fromisoformat(slot.replace("Z", "+00:00")).strftime('%d%H%M')
        if timestamp_key in prices:
            del prices[timestamp_key]
    return prices



def combine_consecutive_slots(actions):
    if not actions:
        return []

    combined_actions = []
    current_action = actions[0]
    start_time = datetime.fromisoformat(current_action["time"].replace("Z", "+00:00"))
    end_time = start_time

    for action in actions[1:]:
        action_time = datetime.fromisoformat(action["time"].replace("Z", "+00:00"))
        if action_time == end_time + timedelta(minutes=5):
            end_time = action_time
        else:
            combined_actions.append({
                "action": current_action["action"],
                "car": current_action["car"],
                "start_time": start_time.isoformat(),
                "end_time": end_time.isoformat()
            })
            current_action = action
            start_time = action_time
            end_time = start_time

    combined_actions.append({
        "action": current_action["action"],
        "car": current_action["car"],
        "start_time": start_time.isoformat(),
        "end_time": (end_time + timedelta(minutes=5)).isoformat()
    })

    return combined_actions

def run_planner(prices, car_id, required_cycles, parking_space, deadline):
    planner_path = 'C:\\Planner\\downward-main\\downward-main\\fast-downward.py'
    used_slots = []
    all_plans = []

    for cycle in range(required_cycles):
        command = [
            'python', planner_path,
            '--alias', 'seq-sat-lama-2011',
            DOMAIN_FILE_PATH, PROBLEM_FILE_PATH
        ]

        result = subprocess.run(command, capture_output=True, text=True)
        if result.returncode == 0:
            plan = parse_plan(result.stdout)
            if not plan:
                print("No plan found for cycle:", cycle)
                break

            sorted_plan = sorted(plan, key=lambda x: prices[x['time']]['price'])[0]
            all_plans.append({
                "action": sorted_plan["action"],
                "car": car_id,
                "time": prices[sorted_plan['time']]['timestamp'],
                "parkingSpace": parking_space
            })
            used_slots.append(prices[sorted_plan['time']]['timestamp'])
            prices = remove_used_time_slots(prices, used_slots)
            update_problem_file(prices, [{'id': car_id, 'required_time': 1, 'deadline': deadline, 'parkingSpace': parking_space}])
        else:
            print("Planner Error:\n", result.stderr)
            break

    return all_plans

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
                    "time": time.replace('t', '')  
                })
    return plan

def transform_plan_to_json(plans, prices):
    transformed_plan = []
    parking_spaces = {}

    for entry in plans:
        parking_space = entry["parkingSpace"]
        if parking_space not in parking_spaces:
            parking_spaces[parking_space] = []

        parking_spaces[parking_space].append({
            "action": entry["action"],
            "car": entry["car"],
            "time": entry["time"]
        })

    for space, actions in parking_spaces.items():
        actions.sort(key=lambda x: x["time"])
        combined_actions = combine_consecutive_slots(actions)
        transformed_plan.append({
            "parkingSpace": space,
            "actions": combined_actions
        })

    return transformed_plan

def publish_plan_to_mqtt(plan):
    client = mqtt.Client()
    client.username_pw_set(MQTT_USER, MQTT_PASSWORD)
    client.connect(MQTT_BROKER, MQTT_PORT, 60)
    client.loop_start()
    client.publish(MQTT_TOPIC, json.dumps(plan), qos=1)
    client.loop_stop()
    client.disconnect()

def start_execution(data):
    prices = extract_prices_from_json(data["prices"])
    cars = extract_cars_from_json(data)
    all_plans = []
    if prices:
        for car in cars:
            update_problem_file(prices, [car])
            car_plans = run_planner(prices, car['id'], car['required_time'], car['parkingSpace'], car['deadline'])
            all_plans.extend(car_plans)
    transformed_plan = transform_plan_to_json(all_plans, prices)
    publish_plan_to_mqtt(transformed_plan)

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
