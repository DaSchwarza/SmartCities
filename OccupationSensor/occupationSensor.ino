#include <WiFi.h>
#include <PubSubClient.h>
#include <ArduinoJson.h> 

// HC SR04 pins
// "Left" Pins
const int trigPin = 18;
const int echoPin = 23;
// "Right" Pins
const int trigPin2 = 13;
const int echoPin2 = 14;

// visial led pin
const int ledPin = D9;

// define constants
#define SOUND_SPEED 0.034      /* define sound speed in cm/uS */
#define uS_TO_S_FACTOR 1000000 /* Conversion factor for micro seconds to seconds */

// define variables
unsigned long duration1;
unsigned long duration2;
float distanceCm1;
float distanceCm2;
// WiFi credentials
const char* ssid     = "<>";
const char* password = "<>";
const char* mqtt_user = "<>>";
const char* mqtt_password = "<>";

// MQTT Server details
const char* mqtt_server = "<>";

WiFiClient espClient;
PubSubClient client(espClient);

const char *mac_adress_left = "bef54ca19801";
const char *mac_adress_right = "481930d7ba90";


const int NUM_MEASUREMENTS = 5;
const int MAX_DEVIATION = 50;
const int THRESHOLD_LEFT = 20;
const int THRESHOLD_RIGHT = 20;

void setup_wifi() {
  delay(10);
  Serial.println();
  Serial.print("Connecting to ");
  Serial.println(ssid);

  WiFi.begin(ssid, password);

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  Serial.println("");
  Serial.println("WiFi connected");
  Serial.println("IP address: ");
  Serial.println(WiFi.localIP());
}

void reconnect() {
  while (!client.connected()) {
    Serial.print("Attempting MQTT connection...");
    if (client.connect("ESP32Client", mqtt_user, mqtt_password)) {
      Serial.println("connected");
    } else {
      Serial.print("failed, rc=");
      Serial.print(client.state());
      Serial.println(" try again in 5 seconds");
      delay(5000);
    }
  }
}

void setup() {
  Serial.begin(4800);
  setup_wifi();
  client.setServer(mqtt_server, 1883);

  pinMode(trigPin, OUTPUT);
  pinMode(echoPin, INPUT);
  pinMode(trigPin2, OUTPUT);
  pinMode(echoPin2, INPUT);
  pinMode(LED_BUILTIN, OUTPUT);
}

void loop() {
  if (!client.connected()) {
    reconnect();
  }
  client.loop();

  measure_distance();
  send_mqtt_message();
  delay(2000);
}

void send_mqtt_message() {
  char topic[100];
  char msg[256];

  StaticJsonDocument<256> doc;

  // Message for the left sensor
  sprintf(topic, "/parking/%s", mac_adress_left);
  doc["mac_adress"] = mac_adress_left;
  doc["distance_cm"] = distanceCm1;
  doc["occupied"] = (distanceCm1 <= THRESHOLD_LEFT) ? true : false;
  serializeJson(doc, msg);
  client.publish(topic, msg);

  // Clear JSON document for next message
  doc.clear();

  // Message for the right sensor
  sprintf(topic, "/parking/%s", mac_adress_right);
  doc["mac_adress"] = mac_adress_right;
  doc["distance_cm"] = distanceCm2;
  doc["occupied"] = (distanceCm2 <= THRESHOLD_RIGHT) ? true : false;
  serializeJson(doc, msg);
  client.publish(topic, msg);
}

void measure_distance() {

  Serial.print("Cycle [");
  Serial.println("]");

  int distances1[NUM_MEASUREMENTS];
  int distances2[NUM_MEASUREMENTS];

  for (int i = 0; i < NUM_MEASUREMENTS; i++) {
    digitalWrite(trigPin, LOW);
    delayMicroseconds(2);
    digitalWrite(trigPin, HIGH);
    delayMicroseconds(10);
    digitalWrite(trigPin, LOW);
    duration1 = pulseIn(echoPin, HIGH);
    distances1[i] = duration1 * SOUND_SPEED / 2;
    
    delay(1000);

    digitalWrite(trigPin2, LOW);
    delayMicroseconds(2);
    digitalWrite(trigPin2, HIGH);
    delayMicroseconds(10);
    digitalWrite(trigPin2, LOW);
    duration2 = pulseIn(echoPin2, HIGH);
    distances2[i] = duration2 * SOUND_SPEED / 2;

    Serial.print("[");
    Serial.print(i);
    Serial.print("]: ");
    Serial.print(distances1[i]);
    Serial.print(" | ");
    Serial.println(distances2[i]);
  }

  int totalDistance1 = 0;
  int totalDistance2 = 0;

  for (int i = 0; i < NUM_MEASUREMENTS; i++) {
    totalDistance1 += distances1[i];
    totalDistance2 += distances2[i];
  }

  distanceCm1 = totalDistance1 / NUM_MEASUREMENTS;
  distanceCm2 = totalDistance2 / NUM_MEASUREMENTS;

  // check for deviation (moving vehicle)
  int deviation1 = 0;
  int deviation2 = 0;

  for (int i = 0; i < NUM_MEASUREMENTS; i++) {
    deviation1 += abs(distances1[i] - distanceCm1);
    deviation2 += abs(distances2[i] - distanceCm2);
  }

  deviation1 /= NUM_MEASUREMENTS;
  deviation2 /= NUM_MEASUREMENTS;

  Serial.print("Deveation: ");
  Serial.print(deviation1);
  Serial.print(" | ");
  Serial.println(deviation2);

  if (deviation1 > MAX_DEVIATION) {
    Serial.print("Deviation 1 too much: ");
    Serial.print(deviation1);

    distanceCm1 = 707;
  }

  if (deviation2 > MAX_DEVIATION) {
    Serial.print("Deviation 2 too much: ");
    Serial.print(deviation2);

    distanceCm2 = 707;
  }
  

  Serial.print("[Left] Distance (cm): ");
  Serial.println(distanceCm1);
  Serial.print("[Right] Distance (cm): ");
  Serial.println(distanceCm2);
}