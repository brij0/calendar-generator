from flask import Flask, request, render_template, jsonify, redirect, session
from database import get_db_connection
from google_auth_oauthlib.flow import Flow
from google.oauth2.credentials import Credentials as GoogleCredentials
from googleapiclient.discovery import build
import pathlib
import os

from datetime import datetime

app = Flask(__name__, template_folder='D:/University/All Projects/Time Table project/templates',static_folder='D:/University/All Projects/Time Table project/static')
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
app.secret_key = "YOUR_SUPER_SECRET_KEY_HERE"

#######################
# Google OAuth Setup  #
#######################
GOOGLE_CLIENT_SECRETS_FILE = str(pathlib.Path(__file__).parent / "client_secret.json")
SCOPES = ['https://www.googleapis.com/auth/userinfo.profile', 'https://www.googleapis.com/auth/userinfo.email', 'openid', 'https://www.googleapis.com/auth/calendar']


def credentials_to_dict(credentials):
    """Helper function to store GoogleCredentials in a dict for session."""
    return {
        'token': credentials.token,
        'refresh_token': credentials.refresh_token,
        'token_uri': credentials.token_uri,
        'client_id': credentials.client_id,
        'client_secret': credentials.client_secret,
        'scopes': credentials.scopes
    }

################################
#    Calendar Integration      #
################################
@app.route('/add_to_calendar', methods=['POST'])
def add_to_calendar():
    """
    This route is called when the user clicks "Add to Google Calendar" in events.html.
    It checks if we have events in session and if the user is authorized. 
    If not authorized, it redirects to /authorize.
    Otherwise, it calls /insert_events_to_calendar.
    """
    # Ensure events exist in session
    if 'all_events' not in session:
        return redirect('/')

    # Check credentials
    if 'credentials' not in session:
        return redirect('/authorize')
    else:
        return redirect('/insert_events_to_calendar')


@app.route('/authorize')
def authorize():
    """
    Initiates the OAuth flow with Google.
    """
    flow = Flow.from_client_secrets_file(
        GOOGLE_CLIENT_SECRETS_FILE,
        scopes=SCOPES,
        redirect_uri='http://127.0.0.1:5000/oauth2callback'  # Must match your GCP "Authorized redirect URI"
    )
    authorization_url, state = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true'
    )
    session['state'] = state
    return redirect(authorization_url)


@app.route('/oauth2callback')
def oauth2callback():
    """
    Google redirects here after authorization. We fetch the token and store credentials in the session.
    """
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
    """
    Actually inserts the events from session['all_events'] into the user's Google Calendar.
    """
    # Check credentials
    if 'credentials' not in session:
        return redirect('/authorize')

    # Check if events are present
    if 'all_events' not in session:
        return redirect('/')

    # Rebuild the GoogleCredentials object
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

    # Insert each event into the user's calendar
    for course_key, course_events in all_events.items():
        for e in course_events:
            event_date_str = e.get('event_date')
            time_str = e.get('time')
            if not event_date_str:
                continue
            try:
                date_obj = datetime.strptime(event_date_str, "%Y-%m-%d")  # 2024-12-02 -> datetime(2024, 12, 2)
            except Exception as ex:
                print("Error parsing date:", ex)
                continue
            start_iso = None
            end_iso = None
            time_zone = "America/Toronto" 
            if time_str and '-' in time_str:
                start_time_str, end_time_str = time_str.split('-')
                try:
                    # Parse "11:30" -> datetime.time(11, 30)
                    start_time_obj = datetime.strptime(start_time_str.strip(), "%H:%M").time()
                    end_time_obj   = datetime.strptime(end_time_str.strip(),   "%H:%M").time()

                    start_dt = datetime.combine(date_obj.date(), start_time_obj)
                    end_dt   = datetime.combine(date_obj.date(), end_time_obj)

                    start_iso = start_dt.isoformat()  
                    end_iso   = end_dt.isoformat()    
                except Exception as ex:
                    print("Error parsing time:", ex)

            if not start_iso or not end_iso:
                start_iso = date_obj.date().isoformat()  # "2024-12-02"
                end_iso = date_obj.date().isoformat()    # same day, or next day if you want 1-day event
                if e['weightage'] != None:
                    description = e['description'] + e['weightage']
                else:
                    description = e['description']
                event_body = {
                    'summary': f"{course_key} - {e['event_type']}",
                    'location': e['location'],
                    'description': description,
                    'start': {
                        'date': start_iso  # For all-day event
                    },
                    'end': {
                        'date': end_iso    # For all-day event
                    },
                    'reminders': {
                        'useDefault': False,
                        'overrides': [
                            {'method': 'email', 'minutes': 24 * 60},
                            {'method': 'popup', 'minutes': 10}
                        ],
                    },
                }
            else:
                # We have valid start/end datetimes
                event_body = {
                    'summary': f"{course_key} - {e['event_type']}",
                    'location': e['location'],
                    'description': e['description'],
                    'start': {
                        'dateTime': start_iso,
                        'timeZone': time_zone
                    },
                    'end': {
                        'dateTime': end_iso,
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

            # Insert into Google Calendar
            service.events().insert(calendarId='primary', body=event_body).execute()

    # Optionally clear the session or show success
    return redirect('/?added_to_calendar=1')


############################################
#          OTHER ROUTES / LOGIC            #
############################################

@app.route('/')
def show_course_types():
    """
    Main landing page to show and search for courses.
    """
    connection, cursor = get_db_connection()
    cursor.execute("SELECT DISTINCT course_type FROM courses ORDER BY course_type ASC")
    course_types = [row[0] for row in cursor.fetchall()]
    cursor.close()
    connection.close()
    return render_template('index.html', course_types=course_types)

@app.route('/get_course_codes', methods=['POST'])
def fetch_course_codes():
    """
    AJAX endpoint to fetch course codes based on selected course type.
    """
    course_type = request.json.get('course_type')
    connection, cursor = get_db_connection()
    cursor.execute("""
        SELECT DISTINCT course_code 
        FROM courses 
        WHERE course_type = %s 
        ORDER BY course_code ASC
    """, (course_type,))
    course_codes = [row[0] for row in cursor.fetchall()]
    cursor.close()
    connection.close()
    return jsonify(course_codes)

@app.route('/course_selection')
def course_selection():
    return render_template('course_selection.html')

@app.route('/top_3_features')
def top_3_features():
    return render_template('features.html')

@app.route('/upcoming_features')
def upcoming_features():
    return render_template('upcoming_features.html')


@app.route('/get_section_numbers', methods=['POST'])
def fetch_section_numbers():
    """
    AJAX endpoint to fetch section numbers based on course type and code.
    """
    course_type = request.json.get('course_type')
    course_code = request.json.get('course_code')

    if not course_type or not course_code:
        return jsonify({"error": "Missing required fields"}), 400

    connection, cursor = get_db_connection()
    try:
        query = """
            SELECT DISTINCT section_number
            FROM courses
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
    # Debug: Log the received form data
    print(request.form)
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
            all_events.update(course_events)
        
        i += 1

    # Store the events in session so /add_to_calendar can access them
    session['all_events'] = all_events
    return render_template('events.html', events=all_events)

def fetch_course_events(course_type, course_code, section_number):
    """
    Helper function to query events for a specific course/section.
    We assume the DB stores dates in 'YYYY-MM-DD' format and times in 'HH:mm-HH:mm'.
    """
    connection, cursor = get_db_connection()
    try:
        query = """
            SELECT e.event_type, 
                   e.event_date,
                   e.start_date,  
                   e.end_date,    
                   e.days,
                   e.time,        
                   e.location,
                   e.description,
                   e.weightage
            FROM course_events e
            JOIN courses c ON e.course_id = c.course_id
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
                'event_date': str(row[1]) if row[1] else None,  # ensure it's a string like "2024-12-02"
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
        return {key: events}
    except Exception as e:
        print(f"Error fetching course events: {e}")
        return {}
    finally:
        cursor.close()
        connection.close()

@app.route('/submit_suggestion', methods=['POST'])
def submit_suggestion():
    data = request.get_json()
    suggestion = data.get("suggestion")

    if not suggestion:
        return jsonify({"error": "Suggestion is required"}), 400

    try:
        # Assuming you have a get_db_connection function
        connection, cursor = get_db_connection()

        # Correct SQL query with placeholders
        query = "INSERT INTO suggestions (suggestion) VALUES (%s)"
        cursor.execute(query, (suggestion,))

        # Commit the transaction and close the connection
        connection.commit()
        connection.close()

        print(f"Inserted suggestion: {suggestion}")
        return jsonify({"message": "Suggestion submitted successfully"}), 200
    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500


@app.route('/upload_course_outline', methods=['POST'])

def upload_course_outline():
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    UPLOAD_FOLDER = '../Sample Course Outlines'
    course_type = request.form.get('course_type')
    course_code = request.form.get('course_code')
    file = request.files.get('course_outline')

    if not course_type or not course_code or not file:
        return jsonify({"error": "Missing fields"}), 400

    # Ensure the upload folder exists
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)

    # Save the file with the naming convention
    filename = f"{course_type}_{course_code}.pdf"
    file_path = os.path.join(UPLOAD_FOLDER, filename)

    try:
        if os.path.exists(file_path):
            return jsonify({"message": "Course already exist please check the dropdown again"}), 200
        else:
            print(f"Saving file to: {os.path.abspath(file_path)}")
            file.save(file_path)
            return jsonify({"message": "Course outline uploaded successfully"}), 200
    except Exception as e:
        return jsonify({"error": f"File saving failed: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(debug=True)
