import mysql.connector
import os
from dotenv import load_dotenv
from timetable import *
from scrape_course import *
import re

def get_db_connection():
    """
    Connect to the MySQL database using the credentials from environment variables.
    Returns:
        db_connection: A connection object to the MySQL database.
        db_cursor: A cursor object to execute queries.
    """
    # Load environment variables
    load_dotenv()
    try:
        db_connection = mysql.connector.connect(
            host=os.getenv("DB_HOST"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            database=os.getenv("DB_NAME")
        )
        db_cursor = db_connection.cursor()
        print("Connected to the database successfully!")
        return db_connection, db_cursor
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return None, None
    
def insert_cleaned_sections(courses_data):
    """
    Clean and add scraped course sections and their associated events to the database.
    Matches the MySQL schema with specific field lengths and constraints.

    Args:
        courses_data (dict): Dictionary with course codes as keys and lists of section info as values
    """
    # Mapping for days abbreviation to full names
    days_mapping = {
        "M": "Monday",
        "T": "Tuesday",
        "W": "Wednesday",
        "Th": "Thursday",
        "F": "Friday",
        "Sa": "Saturday",
        "Su": "Sunday"
    }

    db_connection, db_cursor = get_db_connection()

    try:
        # Process each course and its sections
        for course_code, sections in courses_data.items():
            if sections:
                for course_section in sections:
                    # Clean and truncate section data
                    section_name_cleaned = course_section.get('section_name', '')[:20]  # VARCHAR(50)
                    seats_info = course_section.get('seats', '0/0')[:20]  # VARCHAR(50)
                    instructors_list = ', '.join(course_section.get('instructors', ['Unknown']))[:50]  # VARCHAR(50)
                    course_type_cleaned = course_section.get('course_type', 'Unknown')[:20]  # VARCHAR(50)
                    course_code_cleaned = course_section.get('course_code', '')[:20]  # VARCHAR(50)
                    section_number_cleaned = course_section.get('section_number', '')[:20]  # VARCHAR(50)

                    # Insert section into database
                    insert_section_query = """
                        INSERT INTO test_courses (section_name, seats, instructor, course_type, course_code, section_number)
                        VALUES (%s, %s, %s, %s, %s, %s)
                    """
                    db_cursor.execute(insert_section_query, (section_name_cleaned, seats_info, instructors_list, course_type_cleaned, course_code_cleaned, section_number_cleaned))

                    # Get the last inserted course_id
                    inserted_course_id = db_cursor.lastrowid

                    # Process and clean meeting details
                    meetings_details = course_section.get('meeting_details', [])
                    for meeting_detail in meetings_details:
                        # Clean event data
                        # Clean times
                        meeting_times = meeting_detail.get('times', [])
                        if meeting_times:
                            meeting_times_str = ', '.join(meeting_times) if isinstance(meeting_times, list) else str(meeting_times)
                            match = re.match(r"([MTWThFSu/]+)([0-9:AMP-]+)", meeting_times_str)
                            if match:
                                days_abbreviation = match.group(1)
                                time_details = match.group(2)

                                expanded_days_list = [days_mapping.get(day, day) for day in days_abbreviation.split('/')]
                                expanded_days_string = ', '.join(expanded_days_list)

                                remaining_time_details = meeting_times_str.replace(match.group(0), "").replace("TBD", "").strip()
                                meeting_times = f"{expanded_days_string}, {time_details} {remaining_time_details}".strip(", ")
                            else:
                                meeting_times = meeting_times_str.replace("TBD", "").strip()

                        # Clean location
                        meeting_locations = meeting_detail.get('locations', [])
                        meeting_location_cleaned = (meeting_locations[0] if isinstance(meeting_locations, list) and meeting_locations else str(meeting_locations)).replace('TBD', '').strip()[:255]

                        # Clean event type
                        event_type_cleaned = meeting_detail.get('event_type', 'Unknown').replace('TBD', '').strip()[:50]

                        # Skip events with event_type "Unknown"
                        if event_type_cleaned.lower() == 'unknown':
                            continue

                        # Insert event into database
                        insert_event_query = """
                            INSERT INTO test_events (course_id, event_type, times, location)
                            VALUES (%s, %s, %s, %s)
                        """
                        db_cursor.execute(insert_event_query, (inserted_course_id, event_type_cleaned, meeting_times, meeting_location_cleaned))

                print(f"Processed {len(sections)} sections for course: {course_code}")
            else:
                print(f"No sections found for course: {course_code}")

        # Commit the transaction
        db_connection.commit()
        print("Successfully added all cleaned sections and events to the database")

    except Exception as e:
        print(f"An error occurred while adding data to the database: {e}")
        db_connection.rollback()

    finally:
        db_cursor.close()
        db_connection.close()

def batch_insert_events(events_list, course_id):
    """
    Insert multiple events into the course_events table in one batch operation.
    """
    db_connection, db_cursor = get_db_connection()
    query = """
        INSERT INTO test_course_events (
            course_id, event_type, event_date, start_date, end_date, days, time, location, description, weightage
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """

    # Prepare the data for batch insertion
    batch_data = [
        (
            course_id,
            event.get('event_type'),
            event.get('date'),
            event.get('start_date'),
            event.get('end_date'),
            ','.join(event.get('days', [])),
            event.get('time'),
            event.get('location'),
            event.get('description'),
            event.get('weightage')
        )
        for event in events_list
    ]

    try:
        # Use executemany for batch insertion
        db_cursor.executemany(query, batch_data)
        db_connection.commit()
        print(f"Inserted {db_cursor.rowcount} events for course ID {course_id}.")
    except Exception as e:
        print(f"An error occurred while inserting events: {e}")
        db_connection.rollback()
    finally:
        db_cursor.close()
        db_connection.close()

def get_section_details(school_code, course_code, section_number):
    """
    Extract section information (event type, times, location) and course_id for a specific course and section.

    Args:
        school_code (str): School code (e.g., ENGG).
        course_code (str): Course code (e.g., 3450).
        section_number (str): Section number (e.g., 0201).

    Returns:
        dict: A dictionary with the course_id, course code, and a list of dictionaries containing event_type, times, and location for the section.
    """
    full_section_code = f"{school_code}*{course_code}*{section_number}"
    db_connection, db_cursor = get_db_connection()

    try:
        query = """
            SELECT c.course_id, e.event_type, e.times, e.location
            FROM test_events e
            JOIN test_courses c ON e.course_id = c.course_id
            WHERE c.section_name = %s
        """
        db_cursor.execute(query, (full_section_code,))
        query_results = db_cursor.fetchall()

        # Extract course_id and section information
        section_details = {
            'course_id': None,  # Initialize with None in case no data is found
            'section_details': []
        }

        for result_row in query_results:
            if section_details['course_id'] is None:
                section_details['course_id'] = result_row[0]  # Set course_id from the first row
            section_details['section_details'].append({
                'event_type': result_row[1],
                'times': result_row[2],
                'location': result_row[3]
            })

        return section_details
    except Exception as e:
        print(f"Database error: {e}")
        return {'course_id': None, 'section_details': []}
    finally:
        db_cursor.close()
        db_connection.close()
