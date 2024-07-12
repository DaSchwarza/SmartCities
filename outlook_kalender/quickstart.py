import datetime
import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/calendar.readonly"]

def get_calendar_list(service):
    calendar_list = service.calendarList().list().execute()
    calendars = calendar_list.get('items', [])
    calendar_dict = {calendar['summary']: calendar['id'] for calendar in calendars}
    return calendar_dict

def get_events(service, calendar_id, calendar_name):
    now = datetime.datetime.utcnow().isoformat() + "Z"  # 'Z' indicates UTC time
    print(f"Getting all upcoming events for calendar: {calendar_name}")
    events_result = (
        service.events()
        .list(
            calendarId=calendar_id,
            timeMin=now,
            singleEvents=True,
            orderBy="startTime",
        )
        .execute()
    )
    events = events_result.get("items", [])

    if not events:
        print("No upcoming events found.")
        return

    # Prints the start and end time of all upcoming events
    for event in events:
        start = event["start"].get("dateTime", event["start"].get("date"))
        end = event["end"].get("dateTime", event["end"].get("date"))
        print(f"Start: {start}, End: {end}")

def main():
    """Shows basic usage of the Google Calendar API.
    Prints the start and end time of all upcoming events on the user's calendar.
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

        # Specify the calendar names you are interested in
        calendar_names_of_interest = ["car 1", "car 2"]

        for calendar_name in calendar_names_of_interest:
            if calendar_name in calendar_dict:
                get_events(service, calendar_dict[calendar_name], calendar_name)
            else:
                print(f"Calendar with name '{calendar_name}' not found.")

    except HttpError as error:
        print(f"An error occurred: {error}")

if __name__ == "__main__":
    main()


