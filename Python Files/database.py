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
        
        print("Connected to the database successfully!")
        return connection
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return None
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
        "S": "Saturday",
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
                        INSERT INTO courses (section_name, seats, instructor, course_type, course_code, section_number)
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
                            INSERT INTO events (course_id, event_type, times, location)
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


def extract_section_info(school, course_code, section_number):
    """
    Extract section information (event type, times, location) for a specific course and section.

    Args:
        school (str): School code (e.g., ENGG).
        course_code (str): Course code (e.g., 3450).
        section_number (str): Section number (e.g., 0201).

    Returns:
        list: A list of dictionaries containing event_type, times, and location for the section.
    """
    # Combine the input values into the full section name
    course_code = school + "*" + course_code + "*" + section_number
    # Connect to the database
    connection, cursor = connect_to_database()

    try:
        # Query to extract event information
        query = """
            SELECT event_type, times, location
            FROM events
            WHERE course_id = (
                SELECT course_id
                FROM courses
                WHERE section_name = %s
            )
        """
        
        # Execute the query with the section_name parameter as a tuple
        cursor.execute(query, (course_code,))  # Wrap course_code in a tuple
        
        # Fetch all results
        rows = cursor.fetchall()

        # Convert the results to a list of dictionaries
        column_names = [desc[0] for desc in cursor.description]
        results = [dict(zip(column_names, row)) for row in rows]

        return results

    except Exception as e:
        print(f"An error occurred while extracting section info: {e}")
        return []

    finally:
        # Close the cursor and connection
        cursor.close()
        connection.close()