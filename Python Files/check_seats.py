from seleniumbase import SB
from bs4 import BeautifulSoup
from database import *

def init_selenium_driver():
    """
    Initialize the SeleniumBase driver with specific settings.
    
    Returns:
        SB: An instance of SeleniumBase driver.
    """
    return SB(uc=True, browser="Chrome", incognito=True)


def extract_course_sections_for_seats(course_html):
    """
    Extract relevant course details from HTML content.
    
    Args:
        html (str): The HTML content of the course page.
    
    Returns:
        list: A list of dictionaries containing course section details.
    """
    soup = BeautifulSoup(course_html, 'html.parser')
    tables = soup.find_all('table', class_='esg-table esg-table--no-mobile esg-section--margin-bottom search-sectiontable')
    sections = []  # Changed from dict to list since we're appending, not using section names as keys
    print(f"Found {len(tables)} tables on the page")
    
    for table in tables:
        section_info = {}

        caption = table.find('caption', class_='offScreen')
        if caption:
            section_info['section_name'] = caption.get_text(strip=True)
            section_info['course_type'] = caption.get_text(strip=True).split("*")[0]
            section_info['course_code'] = caption.get_text(strip=True).split("*")[1]
            section_info['section_number'] = caption.get_text(strip=True).split("*")[-1]
        seats_td = table.find('td', class_='search-seatscell')
        if seats_td:
            seat_info = seats_td.find('span', class_='search-seatsavailabletext')
            section_info['seats'] = seat_info.get_text(strip=True) if seat_info else 'Unavailable'

        rows = table.find_all('tr', class_='search-sectionrow')
        meeting_details = []

        for row in rows:
            meeting_info = {}
            time_td = row.find('td', class_='search-sectiondaystime')
            if time_td:
                time_divs = time_td.find_all('div')
                meeting_info['times'] = [time_div.get_text(strip=True) for time_div in time_divs]
            location_td = row.find('td', class_='search-sectionlocations')
            if location_td:
                location_divs = location_td.find_all('div')
                meeting_info['locations'] = [location_div.get_text(strip=True) for location_div in location_divs]

                event_type = location_td.find('span', class_='search-meetingtimestext', id=lambda x: x and 'meeting-instructional-method' in x)
                meeting_info['event_type'] = event_type.get_text(strip=True) if event_type else 'Unknown'

            meeting_details.append(meeting_info)

        instructor_td = table.find('td', class_='search-sectioninstructormethods')
        instructors = []
        if instructor_td:
            instructor_spans = instructor_td.find_all('span')
            for instructor_span in instructor_spans:
                instructors.append(instructor_span.get_text(strip=True))

        section_info['meeting_details'] = meeting_details
        section_info['instructors'] = instructors

        sections.append(section_info)  # Append to list instead of dict
        
    return sections

def scrape_courses(list_of_courses):
    """
    Scrape multiple courses and return their section information.

    Args:
        list_of_courses (list): A list of course codes to scrape

    Returns:
        dict: Dictionary with course codes as keys and lists of section info as values
    """
    scraped_courses = {}
    base_url = 'https://colleague-ss.uoguelph.ca/Student/Courses/Search?keyword={}'
    
    with SB(browser="chrome") as sb:
        for course in list_of_courses:
            url = base_url.format(course)
            try:
                sb.open(url)
                button_selector = f'button[aria-controls="collapsible-view-available-sections-for-{course}-collapseBody"]'
                sb.click(button_selector, timeout=10, delay=0.01)
                sb.wait(5)
                page_source = sb.get_page_source()
                scraped_courses[course] = extract_course_sections_for_seats(page_source)
            except Exception as e:
                print(f"An error occurred while scraping course sections for {course}: {e}")
                scraped_courses[course] = []  # Add empty list for failed courses
                continue
    
    return scraped_courses

def insert_cleaned_sections_into_seats(courses_data):
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
                        INSERT INTO table_for_seat_availability (section_name, seats, instructor, course_type, course_code, section_number)
                        VALUES (%s, %s, %s, %s, %s, %s)
                    """
                    db_cursor.execute(insert_section_query, (section_name_cleaned, seats_info, instructors_list, course_type_cleaned, course_code_cleaned, section_number_cleaned))
        # Commit the transaction
        db_connection.commit()
        print("Successfully added all cleaned sections and events to the database")

    except Exception as e:
        print(f"An error occurred while adding data to the database: {e}")
        db_connection.rollback()

    finally:
        db_cursor.close()
        db_connection.close()