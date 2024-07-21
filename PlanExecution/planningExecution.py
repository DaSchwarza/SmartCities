import paho.mqtt.client as mqtt
import time
from datetime import datetime, timezone
import json
import logging
import os

# Logging einrichten
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Konfiguration des MQTT-Brokers (kann über Umgebungsvariablen gesetzt werden)
MQTT_BROKER = os.getenv("MQTT_BROKER", "167.172.166.109")
MQTT_PORT = int(os.getenv("MQTT_PORT", 1883))
MQTT_USER = os.getenv("MQTT_USER", "local")
MQTT_PASSWORD = os.getenv("MQTT_PASSWORD", "Stuttgart")
MQTT_TOPIC = os.getenv("MQTT_TOPIC", "/standardized/plan/created")
MQTT_PLAN_TOPIC = os.getenv("MQTT_PLAN_TOPIC","/standardized/plan/create")

# Globale Variablen zur Speicherung des Plans und des Ladestatus
plan = [] 
is_charging = {}

# Callback, wenn die Verbindung zum MQTT-Broker hergestellt wird
def on_connect(client, userdata, flags, rc):
    logger.info(f"Verbunden mit MQTT-Broker, Ergebniscode: {rc}")
    client.subscribe(MQTT_TOPIC)
    client.subscribe(MQTT_PLAN_TOPIC)

# Callback, wenn eine Nachricht vom MQTT-Broker empfangen wird
def on_message(client, userdata, msg):
    if msg.topic == MQTT_TOPIC:
        global plan
        global is_charging
        logger.info(f"Nachricht empfangen: {msg.topic} {msg.payload}")
        if msg.topic == MQTT_TOPIC:
            plan = json.loads(msg.payload)
            logger.info(f"Plan aktualisiert: {plan}")
            for car_plan in plan:
                parking_space = car_plan.get("parkingSpace")
                # Deaktivieren des Steckers sofort nach Erhalt des neuen Plans
                if is_charging.get(parking_space, False):
                    send_mqtt_command(client, parking_space, False)
                    is_charging[parking_space] = False
                    logger.info(f"Steckdose für Parkplatz {parking_space} deaktiviert")
                is_charging[parking_space] = False
    elif msg.topic == MQTT_PLAN_TOPIC:
        data = json.loads(msg.payload)
        send_mqtt_command(client, data['data']['car']['parkingSpace'], False)
        # Laden ausschalten, bis neuer Plan fertig ist

# Funktion zum Senden von MQTT-Befehlen zum Starten oder Stoppen des Ladevorgangs
def send_mqtt_command(client, parking_space_id, command):
    message = {
        "enabled": command
    }
    topic = f"/standardized/execute/{parking_space_id}"
    client.publish(topic, json.dumps(message))
    logger.info(f"MQTT-Nachricht gesendet: {json.dumps(message)} zu Topic: {topic}")

# Hauptfunktion zur Ausführung des Plans durch Überprüfung der aktuellen Zeit mit den Planaktionen
def execute_plan():
    client = mqtt.Client()
    client.username_pw_set(MQTT_USER, MQTT_PASSWORD)
    client.on_connect = on_connect
    client.on_message = on_message

    client.connect(MQTT_BROKER, MQTT_PORT, 60)
    client.loop_start()

    global is_charging
    last_action_time = {}

    logger.info("Plan-Ausführung gestartet")
    while True:
        current_time = datetime.now(timezone.utc).replace(second=0, microsecond=0)
        current_time_iso = current_time.isoformat()
        logger.info(f"Aktuelle UTC-Zeit: {current_time_iso}")
        for parking_space_entry in plan:
            parking_space = parking_space_entry["parkingSpace"]
            for action in parking_space_entry["actions"]:
                try:
                    start_time_iso = action["start_time"]
                    end_time_iso = action["end_time"]
                    start_time = datetime.fromisoformat(start_time_iso).replace(second=0, microsecond=0)
                    end_time = datetime.fromisoformat(end_time_iso).replace(second=0, microsecond=0)
                    logger.info(f"Überprüfe Aktion {action['action']} von {start_time_iso} bis {end_time_iso} für Parkplatz {parking_space}")
                    
                    if start_time <= current_time < end_time:  # Aktuelle Zeit liegt im Aktionszeitraum
                        logger.info(f"Aktion {action['action']} ist aktiv um {current_time_iso}")
                        
                        if action["action"] == "start-charging":
                            # Überprüfen, ob das Laden für diesen Parkplatz bereits aktiv ist
                            if not is_charging.get(parking_space, False):
                                send_mqtt_command(client, parking_space, True)
                                is_charging[parking_space] = True
                                last_action_time[parking_space] = start_time
                                logger.info(f"Laden für Parkplatz {parking_space} gestartet")
                        
                        elif action["action"] == "stop-charging":
                            # Überprüfen, ob das Laden für diesen Parkplatz derzeit aktiv ist
                            if is_charging.get(parking_space, False):
                                send_mqtt_command(client, parking_space, False)
                                is_charging[parking_space] = False
                                logger.info(f"Laden für Parkplatz {parking_space} gestoppt")
                    elif start_time < current_time and not is_charging.get(parking_space, False):
                        # Laden sofort starten, wenn die Startzeit in der Vergangenheit liegt
                        send_mqtt_command(client, parking_space, True)
                        is_charging[parking_space] = True
                        last_action_time[parking_space] = start_time
                        logger.info(f"Laden sofort gestartet für Parkplatz {parking_space} aufgrund der Startzeit in der Vergangenheit")
                except KeyError as e:
                    logger.error(f"KeyError: {e}. Aktion: {action}")
        time.sleep(5) 

if __name__ == "__main__":
    execute_plan()
