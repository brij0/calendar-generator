from http import client
from flask import Flask, request, render_template, jsonify
from database import *
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.auth.transport.requests import AuthorizedSession
from flask import url_for, redirect
from flask import Flask, redirect, request, url_for, session
from google_auth_oauthlib.flow import Flow
from google.oauth2.credentials import Credentials
import os
import json

app = Flask(__name__, template_folder='D:/University/All Projects/Time Table project/templates')

@app.route('/')
def show_course_types():
    connection, cursor = get_db_connection()
    cursor.execute("SELECT DISTINCT course_type FROM test_courses ORDER BY course_type ASC")
    course_types = [row[0] for row in cursor.fetchall()]
    return render_template('index.html', course_types=course_types)

@app.route('/get_course_codes', methods=['POST'])
def fetch_course_codes():
    course_type = request.json.get('course_type')
    connection, cursor = get_db_connection()
    cursor.execute("SELECT DISTINCT course_code FROM test_courses WHERE course_type = %s ORDER BY course_code ASC", (course_type,))
    course_codes = [row[0] for row in cursor.fetchall()]
    return jsonify(course_codes)

@app.route('/about')
def show_about_page():
    return render_template('about.html')

@app.route('/get_section_numbers', methods=['POST'])
def fetch_section_numbers():
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
    all_events = {}

    form_data = request.form
    i = 0
    while True:
        course_type = form_data.get(f'course_type_{i}')
        course_code = form_data.get(f'course_code_{i}')
        section_number = form_data.get(f'section_number_{i}')
        
        if not any([course_type, course_code, section_number]):
            break
            
        if all([course_type, course_code, section_number]):
            course_events = fetch_course_events(course_type, course_code, section_number)
            all_events.update(course_events)  # Combine dictionaries
            
        i += 1
    
    return render_template('events.html', events=all_events)


def fetch_course_events(course_type, course_code, section_number):
    connection, cursor = get_db_connection()
    try:
        query = """
            SELECT e.event_type, e.event_date, e.start_date, e.end_date, e.days, e.time, e.location, e.description, e.weightage
            FROM test_course_events e
            JOIN test_courses c ON e.course_id = c.course_id
            WHERE c.course_type = %s AND c.course_code = %s AND c.section_number = %s
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
        
        key = f"{course_type}*{course_code}*{section_number}"
        return {key: events}  # Return a dictionary
    except Exception as e:
        print(f"Error fetching course events: {e}")
        return {}
    finally:
        cursor.close()
        connection.close()


# Disable HTTPS requirement for local development
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'



GOOGLE_CLIENT_CONFIG = {
    "web": {
        "client_id": os.getenv("google_client_id"),
        "client_secret": os.getenv("google_client_secret"),
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "redirect_uris": ["http://localhost:5000/oauth2callback"]
    }
}

@app.route('/authorize')
def authorize():
    # Create flow instance to manage the OAuth 2.0 Authorization Grant Flow steps.
    flow = Flow.from_client_config(
        GOOGLE_CLIENT_CONFIG,
        scopes=['https://www.googleapis.com/auth/calendar'],
        redirect_uri=url_for('oauth2callback', _external=True)
    )
    
    # Generate URL for request to Google's OAuth 2.0 server.
    authorization_url, state = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true'
    )
    
    # Store the state so the callback can verify the auth server response.
    session['state'] = state
    
    return redirect(authorization_url)

@app.route('/oauth2callback')
def oauth2callback():
    # Specify the state when creating the flow in the callback so that it can
    # verify the authorization server response.
    state = session['state']
    
    flow = Flow.from_client_config(
        GOOGLE_CLIENT_CONFIG,
        scopes=['https://www.googleapis.com/auth/calendar'],
        state=state,
        redirect_uri=url_for('oauth2callback', _external=True)
    )
    
    # Use the authorization server's response to fetch the OAuth 2.0 tokens.
    authorization_response = request.url
    flow.fetch_token(authorization_response=authorization_response)
    
    # Store credentials in the session.
    credentials = flow.credentials
    session['credentials'] = {
        'token': credentials.token,
        'refresh_token': credentials.refresh_token,
        'token_uri': credentials.token_uri,
        'client_id': credentials.client_id,
        'client_secret': credentials.client_secret,
        'scopes': credentials.scopes
    }
    
    return redirect(url_for('calendar_page'))

def get_google_credentials():
    if 'credentials' not in session:
        return redirect(url_for('authorize'))
        
    # Load credentials from session
    credentials = Credentials(
        token=session['credentials']['token'],
        refresh_token=session['credentials']['refresh_token'],
        token_uri=session['credentials']['token_uri'],
        client_id=session['credentials']['client_id'],
        client_secret=session['credentials']['client_secret'],
        scopes=session['credentials']['scopes']
    )
    
    return credentials

# Function to add events to Google Calendar
@app.route('/add_to_calendar', methods=['POST'])
def add_events_to_calendar():
    try:
        # Verify content type
        if not request.is_json:
            return jsonify({"error": "Content-Type must be application/json"}), 415

        # Get events from the POST request
        data = request.get_json()
        events = data.get('events')
        
        if not events:
            return jsonify({"error": "No events provided"}), 400

        # Authenticate and build the Google Calendar API service
        credentials = get_google_credentials()
        authed_session = AuthorizedSession(credentials)
        service = build('calendar', 'v3', credentials=credentials, request=authed_session)
        service = build('calendar', 'v3', credentials=credentials)

        added_events = []
        for event in events:
            # Validate required fields
            required_fields = ['event_type', 'location', 'event_date', 'time']
            if not all(field in event for field in required_fields):
                return jsonify({"error": f"Missing required fields: {required_fields}"}), 400

            # Parse time properly
            try:
                start_time, end_time = event['time'].split('-')
                start_datetime = f"{event['event_date']}T{start_time.strip()}:00"
                end_datetime = f"{event['event_date']}T{end_time.strip()}:00"
            except ValueError:
                return jsonify({"error": "Invalid time format"}), 400

            calendar_event = {
                'summary': event['event_type'],
                'location': event['location'],
                'description': event.get('description', ''),
                'start': {
                    'dateTime': start_datetime,
                    'timeZone': 'America/Toronto',
                },
                'end': {
                    'dateTime': end_datetime,
                    'timeZone': 'America/Toronto',
                }
            }
            
            result = service.events().insert(calendarId='primary', body=calendar_event).execute()
            added_events.append(result['id'])

        return jsonify({
            "success": True,
            "message": "Events added to Google Calendar",
            "event_ids": added_events
        }), 200

    except Exception as e:
        app.logger.error(f"Error adding events to Google Calendar: {str(e)}")
        return jsonify({
            "success": False,
            "error": "Failed to add events to calendar",
            "details": str(e)
        }), 500


if __name__ == '__main__':
    app.run(debug=True)