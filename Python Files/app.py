from flask import Flask, request, render_template, jsonify
from database import *
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from flask import url_for, redirect

app = Flask(__name__, template_folder='D:/University/All Projects/Time Table project/templates')

@app.route('/')
def index():
    connection, cursor = connect_to_database()
    cursor.execute("SELECT DISTINCT course_type FROM test_courses ORDER BY course_type ASC")
    course_types = [row[0] for row in cursor.fetchall()]
    return render_template('index.html', course_types=course_types)

@app.route('/get_course_codes', methods=['POST'])
def get_course_codes():
    course_type = request.json.get('course_type')
    connection, cursor = connect_to_database()
    cursor.execute("SELECT DISTINCT course_code FROM test_courses WHERE course_type = %s ORDER BY course_code ASC", (course_type,))
    course_codes = [row[0] for row in cursor.fetchall()]
    return jsonify(course_codes)

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/get_section_numbers', methods=['POST'])
def get_section_numbers():
    course_type = request.json.get('course_type')
    course_code = request.json.get('course_code')

    if not course_type or not course_code:
        return jsonify({"error": "Missing required fields"}), 400

    connection, cursor = connect_to_database()
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
def search_course():
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
            course_events = get_course_events(course_type, course_code, section_number)
            all_events.update(course_events)  # Combine dictionaries
            
        i += 1
    
    return render_template('events.html', events=all_events)


def get_course_events(course_type, course_code, section_number):
    connection, cursor = connect_to_database()
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

SCOPES = ['https://www.googleapis.com/auth/calendar'] # Google Calendar API scope

def authenticate_google():
    flow = InstalledAppFlow.from_client_secrets_file(
        'path/to/credentials.json', SCOPES)  # Provide your credentials.json path
    credentials = flow.run_local_server(port=0)
    return credentials

# Function to add events to Google Calendar
@app.route('/add_to_calendar', methods=['POST'])
def add_to_calendar():
    try:
        # Get events from the POST request
        events = request.json.get('events')  # Expecting JSON data with events
        if not events:
            return jsonify({"error": "No events provided"}), 400

        # Authenticate and build the Google Calendar API service
        creds = authenticate_google()
        service = build('calendar', 'v3', credentials=creds)

        # Add each event to Google Calendar
        for event in events:
            calendar_event = {
                'summary': event.get('event_type'),
                'location': event.get('location'),
                'description': event.get('description'),
                'start': {
                    'dateTime': event.get('event_date') + 'T' + event.get('time').split('-')[0] + ':00',
                    'timeZone': 'America/Toronto',
                },
                'end': {
                    'dateTime': event.get('event_date') + 'T' + event.get('time').split('-')[1] + ':00',
                    'timeZone': 'America/Toronto',
                },
            }
            service.events().insert(calendarId='primary', body=calendar_event).execute()

        return jsonify({"success": "Events added to Google Calendar"}), 200
    except Exception as e:
        print(f"Error adding events to Google Calendar: {e}")
        return jsonify({"error": "Failed to add events"}), 500


if __name__ == '__main__':
    app.run(debug=True)