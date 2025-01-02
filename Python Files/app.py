from flask import Flask, request, render_template, jsonify, redirect, session, abort
from database import get_db_connection  # Make sure this exists
from google_auth_oauthlib.flow import Flow
from google.oauth2.credentials import Credentials as GoogleCredentials
from googleapiclient.discovery import build
import google.auth.transport.requests
import os
import pathlib
import requests

app = Flask(__name__, template_folder='D:/University/All Projects/Time Table project/templates')
# 1. You must set a secret key to use sessions
import os 
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
app.secret_key = "YOUR_SUPER_SECRET_KEY_HERE"

#######################
# Google OAuth Setup  #
#######################
GOOGLE_CLIENT_SECRETS_FILE = str(pathlib.Path(__file__).parent / "client_secret.json")
SCOPES = ['https://www.googleapis.com/auth/userinfo.email', 'https://www.googleapis.com/auth/userinfo.profile', 'https://www.googleapis.com/auth/calendar', 'openid']

def credentials_to_dict(credentials):
    return {
        'token': credentials.token,
        'refresh_token': credentials.refresh_token,
        'token_uri': credentials.token_uri,
        'client_id': credentials.client_id,
        'client_secret': credentials.client_secret,
        'scopes': credentials.scopes
    }

########################
# Calendar Integration #
########################
@app.route('/add_to_calendar', methods=['POST'])
def add_to_calendar():
    # Ensure we have events in session
    if 'all_events' not in session:
        return redirect('/')

    # Check credentials
    if 'credentials' not in session:
        # Not authorized yet; go to /authorize
        return redirect('/authorize')
    else:
        # Already have credentials; insert the events
        return redirect('/insert_events_to_calendar')

@app.route('/authorize')
def authorize():
    flow = Flow.from_client_secrets_file(
        GOOGLE_CLIENT_SECRETS_FILE,
        scopes=SCOPES,
        # Make sure this redirect_uri is in your Google Cloud Console
        redirect_uri='http://127.0.0.1:5000/oauth2callback'
    )
    authorization_url, state = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true'
    )
    session['state'] = state
    return redirect(authorization_url)

@app.route('/oauth2callback')
def oauth2callback():
    state = session.get('state')
    flow = Flow.from_client_secrets_file(
        GOOGLE_CLIENT_SECRETS_FILE,
        scopes=SCOPES,
        redirect_uri='http://127.0.0.1:5000/oauth2callback'
    )
    flow.fetch_token(authorization_response=request.url)
    credentials = flow.credentials
    session['credentials'] = credentials_to_dict(credentials)
    return redirect('/insert_events_to_calendar')

@app.route('/insert_events_to_calendar')
def insert_events_to_calendar():
    # If not authorized, go back to /authorize
    if 'credentials' not in session:
        return redirect('/authorize')

    # If no events, go back home
    if 'all_events' not in session:
        return redirect('/')

    # Rebuild credentials
    creds_dict = session['credentials']
    creds = GoogleCredentials(
        token=creds_dict['token'],
        refresh_token=creds_dict.get('refresh_token'),
        token_uri=creds_dict['token_uri'],
        client_id=creds_dict['client_id'],
        client_secret=creds_dict['client_secret'],
        scopes=creds_dict['scopes']
    )
    service = build("calendar", "v3", credentials=creds)

    all_events = session['all_events']

    # For each course and each event, insert into Google Calendar
    for course_key, course_events in all_events.items():
        for e in course_events:
            # TODO: Parse your actual start/end times. Here we use placeholders:
            start_datetime = "2025-01-01T10:00:00"
            end_datetime   = "2025-01-01T12:00:00"
            time_zone      = "Asia/Kolkata"

            event_body = {
                'summary': f"{course_key} - {e['event_type']}",
                'location': e['location'],
                'description': e['description'],
                'start': {
                    'dateTime': start_datetime,
                    'timeZone': time_zone
                },
                'end': {
                    'dateTime': end_datetime,
                    'timeZone': time_zone
                },
                'reminders': {
                    'useDefault': False,
                    'overrides': [
                        {'method': 'email', 'minutes': 24 * 60},
                        {'method': 'popup', 'minutes': 10}
                    ],
                },
            }

            service.events().insert(
                calendarId='primary',
                body=event_body
            ).execute()

    # Redirect to home with an optional message
    return redirect('/?added_to_calendar=1')


#############################
#       OTHER ROUTES        #
#############################

@app.route('/')
def show_course_types():
    """Main landing page to show and search for courses."""
    connection, cursor = get_db_connection()
    cursor.execute("SELECT DISTINCT course_type FROM test_courses ORDER BY course_type ASC")
    course_types = [row[0] for row in cursor.fetchall()]
    cursor.close()
    connection.close()
    return render_template('index.html', course_types=course_types)

@app.route('/get_course_codes', methods=['POST'])
def fetch_course_codes():
    """AJAX endpoint to fetch course codes based on selected course type."""
    course_type = request.json.get('course_type')
    connection, cursor = get_db_connection()
    cursor.execute("""
        SELECT DISTINCT course_code 
        FROM test_courses 
        WHERE course_type = %s 
        ORDER BY course_code ASC
    """, (course_type,))
    course_codes = [row[0] for row in cursor.fetchall()]
    cursor.close()
    connection.close()
    return jsonify(course_codes)

@app.route('/about')
def show_about_page():
    """Render an About page."""
    return render_template('about.html')

@app.route('/get_section_numbers', methods=['POST'])
def fetch_section_numbers():
    """AJAX endpoint to fetch section numbers based on course type and code."""
    course_type = request.json.get('course_type')
    course_code = request.json.get('course_code')

    if not course_type or not course_code:
        return jsonify({"error": "Missing required fields"}), 400

    connection, cursor = get_db_connection()
    try:
        query = """
            SELECT DISTINCT section_number
            FROM test_courses
            WHERE course_type = %s AND course_code = %s
        """
        cursor.execute(query, (course_type, course_code))
        rows = cursor.fetchall()

        section_numbers = [row[0] for row in rows]
        return jsonify(section_numbers)
    except Exception as e:
        print(f"Error fetching section numbers: {e}")
        return jsonify({"error": "Internal server error"}), 500
    finally:
        cursor.close()
        connection.close()

@app.route('/search', methods=['POST'])
def search_courses():
    """Fetch events for each chosen course and display the schedule."""
    all_events = {}
    form_data = request.form
    i = 0

    while True:
        course_type = form_data.get(f'course_type_{i}')
        course_code = form_data.get(f'course_code_{i}')
        section_number = form_data.get(f'section_number_{i}')
        
        # If all three are empty, we've reached the end
        if not any([course_type, course_code, section_number]):
            break

        # If all three exist, fetch the events
        if all([course_type, course_code, section_number]):
            course_events = fetch_course_events(course_type, course_code, section_number)
            # Merge into the all_events dictionary
            all_events.update(course_events)
        
        i += 1

    # 2. Store all_events in the session
    session['all_events'] = all_events

    return render_template('events.html', events=all_events)

def fetch_course_events(course_type, course_code, section_number):
    """Helper function to query events for a specific course/section."""
    connection, cursor = get_db_connection()
    try:
        query = """
            SELECT e.event_type, e.event_date, e.start_date, e.end_date, 
                   e.days, e.time, e.location, e.description, e.weightage
            FROM test_course_events e
            JOIN test_courses c ON e.course_id = c.course_id
            WHERE c.course_type = %s 
              AND c.course_code = %s 
              AND c.section_number = %s
        """
        cursor.execute(query, (course_type, course_code, section_number))
        rows = cursor.fetchall()

        events = []
        for row in rows:
            event = {
                'event_type': row[0],
                'event_date': row[1],
                'start_date': row[2],
                'end_date': row[3],
                'days': row[4],
                'time': row[5],
                'location': row[6],
                'description': row[7],
                'weightage': row[8]
            }
            events.append(event)
        
        # The dict key: "course_type*course_code*section_number"
        key = f"{course_type}*{course_code}*{section_number}"
        return {key: events}
    except Exception as e:
        print(f"Error fetching course events: {e}")
        return {}
    finally:
        cursor.close()
        connection.close()

if __name__ == '__main__':
    app.run(debug=True)
