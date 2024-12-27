from sqlite3 import Cursor
import mysql.connector
import os
from dotenv import load_dotenv
from timetable import *
from scrape_course import *
import re

def connect_to_database():
    """
    Connect to the MySQL database using the credentials from environment variables.
    Returns:
        connection: A connection object to the MySQL database.
        cursor: A cursor object to execute queries.
    """
    # Load environment variables
    load_dotenv()
    try:
        connection = mysql.connector.connect(
            host=os.getenv("DB_HOST"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            database=os.getenv("DB_NAME")
        )
        cursor = connection.cursor()
        print("Connected to the database successfully!")
        return connection, cursor
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return None, None
    
def add_cleaned_section_to_db(course_data):
    """
    Clean and add scraped course sections and their associated events to the database.
    Matches the MySQL schema with specific field lengths and constraints.

    Args:
        course_data (dict): Dictionary with course codes as keys and lists of section info as values
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

    connection, cursor = connect_to_database()

    try:
        # Process each course and its sections
        for course_code, sections in course_data.items():
            if sections:
                for section in sections:
                    # Clean and truncate section data
                    section_name = section.get('section_name', '')[:20]  # VARCHAR(50)
                    seats = section.get('seats', '0/0')[:20]  # VARCHAR(50)
                    instructors = ', '.join(section.get('instructors', ['Unknown']))[:50]  # VARCHAR(50)
                    course_type = section.get('course_type', 'Unknown')[:20]  # VARCHAR(50)
                    course_code = section.get('course_code', '')[:20]  # VARCHAR(50)
                    section_number = section.get('section_number', '')[:20]  # VARCHAR(50)

                    # Insert section into database
                    query1 = """
                        INSERT INTO test_courses (section_name, seats, instructor, course_type, course_code, section_number)
                        VALUES (%s, %s, %s, %s, %s, %s)
                    """
                    cursor.execute(query1, (section_name, seats, instructors, course_type, course_code, section_number))

                    # Get the last inserted course_id
                    course_id = cursor.lastrowid

                    # Process and clean meeting details
                    meeting_details = section.get('meeting_details', [])
                    for meeting in meeting_details:
                        # Clean event data
                        # Clean times
                        times = meeting.get('times', [])
                        if times:
                            times_str = ', '.join(times) if isinstance(times, list) else str(times)
                            match = re.match(r"([MTWThFSu/]+)([0-9:AMP-]+)", times_str)
                            if match:
                                days_part = match.group(1)
                                time_part = match.group(2)

                                expanded_days = [days_mapping.get(day, day) for day in days_part.split('/')]
                                expanded_days_str = ', '.join(expanded_days)

                                rest_part = times_str.replace(match.group(0), "").replace("TBD", "").strip()
                                times = f"{expanded_days_str}, {time_part} {rest_part}".strip(", ")
                            else:
                                times = times_str.replace("TBD", "").strip()

                        # Clean location
                        locations = meeting.get('locations', [])
                        location = (locations[0] if isinstance(locations, list) and locations else str(locations)).replace('TBD', '').strip()[:255]

                        # Clean event type
                        event_type = meeting.get('event_type', 'Unknown').replace('TBD', '').strip()[:50]

                        # Skip events with event_type "Unknown"
                        if event_type.lower() == 'unknown':
                            continue

                        # Insert event into database
                        query2 = """
                            INSERT INTO test_events (course_id, event_type, times, location)
                            VALUES (%s, %s, %s, %s)
                        """
                        cursor.execute(query2, (course_id, event_type, times, location))

                print(f"Processed {len(sections)} sections for course: {course_code}")
            else:
                print(f"No sections found for course: {course_code}")

        # Commit the transaction
        connection.commit()
        print("Successfully added all cleaned sections and events to the database")

    except Exception as e:
        print(f"An error occurred while adding data to the database: {e}")
        connection.rollback()

    finally:
        cursor.close()
        connection.close()




def insert_events_batch(events, course_id):
    """
    Insert multiple events into the course_events table in one batch operation.
    """
    connection, cursor = connect_to_database()
    query = """
        INSERT INTO test_course_events (
            course_id, event_type, event_date, start_date, end_date, days, time, location, description, weightage
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """

    # Prepare the data for batch insertion
    data = [
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
        for event in events
    ]

    try:
        # Use executemany for batch insertion
        cursor.executemany(query, data)
        connection.commit()
        print(f"Inserted {cursor.rowcount} events for course ID {course_id}.")
    except Exception as e:
        print(f"An error occurred while inserting events: {e}")
        connection.rollback()
    finally:
        cursor.close()
        connection.close()


def extract_section_info(school, course_code, section_number):
    """
    Extract section information (event type, times, location) and course_id for a specific course and section.

    Args:
        school (str): School code (e.g., ENGG).
        course_code (str): Course code (e.g., 3450).
        section_number (str): Section number (e.g., 0201).

    Returns:
        dict: A dictionary with the course_id, course code, and a list of dictionaries containing event_type, times, and location for the section.
    """
    full_course_code = f"{school}*{course_code}*{section_number}"
    connection, cursor = connect_to_database()

    try:
        query = """
            SELECT c.course_id, e.event_type, e.times, e.location
            FROM test_events e
            JOIN test_courses c ON e.course_id = c.course_id
            WHERE c.section_name = %s
        """
        cursor.execute(query, (full_course_code,))
        rows = cursor.fetchall()

        # Extract course_id and section information
        section_info = {
            'course_id': None,  # Initialize with None in case no data is found
            'section_details': []
        }

        for row in rows:
            if section_info['course_id'] is None:
                section_info['course_id'] = row[0]  # Set course_id from the first row
            section_info['section_details'].append({
                'event_type': row[1],
                'times': row[2],
                'location': row[3]
            })

        return section_info
    except Exception as e:
        print(f"Database error: {e}")
        return {'course_id': None, 'section_details': []}
    finally:
        cursor.close()
        connection.close()


