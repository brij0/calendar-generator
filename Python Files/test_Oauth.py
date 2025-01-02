from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
scopes = ['https://www.googleapis.com/auth/calendar']
flow = InstalledAppFlow.from_client_secrets_file("client_secret.json", scopes=scopes)
credentials = flow.run_console()
import pickle
pickle.dump(credentials, open("token.pkl", "wb"))
credentials = pickle.load(open("token.pkl", "rb"))
service = build("calendar", "v3", credentials=credentials)

result = service.calendarList().list().execute()
result['items'][0]

calendar_id = result['items'][0]['id']
result = service.events().list(calendarId=calendar_id, timeZone="Asia/Kolkata").execute()
result['items'][0]

from datetime import datetime, timedelta
start_time = datetime(2019, 5, 12, 19, 30, 0)
end_time = start_time + timedelta(hours=4)
timezone = 'Asia/Kolkata'
event = {
  'summary': 'IPL Final 2019',
  'location': 'Hyderabad',
  'description': 'MI vs TBD',
  'start': {
    'dateTime': start_time.strftime("%Y-%m-%dT%H:%M:%S"),
    'timeZone': timezone,
  },
  'end': {
    'dateTime': end_time.strftime("%Y-%m-%dT%H:%M:%S"),
    'timeZone': timezone,
  },
  'reminders': {
    'useDefault': False,
    'overrides': [
      {'method': 'email', 'minutes': 24 * 60},
      {'method': 'popup', 'minutes': 10},
    ],
  },
}
service.events().insert(calendarId=calendar_id, body=event).execute()