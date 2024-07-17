import datetime
import os.path
import json

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import paho.mqtt.client as mqtt

# Source: https://developers.google.com/calendar/api/quickstart/python

SCOPES = ["https://www.googleapis.com/auth/calendar.readonly"]

# MQTT configuration
MQTT_BROKER="167.172.166.109" 
MQTT_PORT=1883
MQTT_USER="local"
MQTT_PASSWORD="Stuttgart"
MQTT_TOPIC = "/standardized/calendar/events"

def get_calendar_list(service):
    calendar_list = service.calendarList().list().execute()
    calendars = calendar_list.get('items', [])
    calendar_dict = {calendar['summary']: calendar['id'] for calendar in calendars}
    return calendar_dict

def get_events(service, calendar_id, calendar_name):
    now = datetime.datetime.utcnow().isoformat() + "Z"  
    print(f"Getting the next 2 upcoming events for calendar: {calendar_name}")
    events_result = (
        service.events()
        .list(
            calendarId=calendar_id,
            timeMin=now,
            maxResults=2,  
            singleEvents=True,
            orderBy="startTime",
        )
        .execute()
    )
    events = events_result.get("items", [])

    if not events:
        print("No upcoming events found.")
        return

    events_data = []
    for event in events:
        start = event["start"].get("dateTime", event["start"].get("date"))
        end = event["end"].get("dateTime", event["end"].get("date"))
        events_data.append({"start": start, "end": end})

    # Publish events to MQTT
    publish_events(calendar_name, events_data)

def publish_events(calendar_name, events_data):
    client = mqtt.Client()
    client.username_pw_set(MQTT_USER, MQTT_PASSWORD)
    client.connect(MQTT_BROKER, MQTT_PORT, 60)
    topic = MQTT_TOPIC + "/" + calendar_name

    payload = json.dumps({
        "events": events_data
    })
    client.publish(topic, payload)
    client.disconnect()
    print(f"Published events for calendar: {calendar_name}")

def main():
    """Shows basic usage of the Google Calendar API.
    Prints the start and end time of the next 2 upcoming events on the user's calendar.
    """
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "credentials.json", SCOPES
            )
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open("token.json", "w") as token:
            token.write(creds.to_json())

    try:
        service = build("calendar", "v3", credentials=creds)

        # Get the list of calendars
        calendar_dict = get_calendar_list(service)

        calendar_names_of_interest = ["F-UN-404", "BI-ER-200"]

        for calendar_name in calendar_names_of_interest:
            if calendar_name in calendar_dict:
                get_events(service, calendar_dict[calendar_name], calendar_name)
            else:
                print(f"Calendar with name '{calendar_name}' not found.")

    except HttpError as error:
        print(f"An error occurred: {error}")

if __name__ == "__main__":
    main()



