from seleniumbase import SB
from bs4 import BeautifulSoup

# Base URL with course code dynamically appended
base_url = 'https://colleague-ss.uoguelph.ca/Student/Courses/Search?keyword='

# Utility function to initialize the SeleniumBase driver
def initialize_driver():
    return SB(uc=True, browser="Chrome", incognito=True)

# Function to scrape course page content using SeleniumBase
def get_course_page(course_code):
    url = base_url + course_code
    with initialize_driver() as sb:
        try:
            # Open the URL and click the required button to reveal sections
            sb.open(url)
            button_selector = f'button[aria-controls="collapsible-view-available-sections-for-{course_code}-collapseBody"]'
            sb.click(button_selector, timeout=10, delay=0.01)
            sb.wait(3)
            # Get and return page source
            return sb.get_page_source()
        except Exception as e:
            print(f"An error occurred while scraping course sections: {e}")
            return None

# Function to extract relevant course details from HTML content
def extract_course_sections_with_type(html):
    soup = BeautifulSoup(html, 'html.parser')

    # Find all course tables in the HTML
    tables = soup.find_all('table', class_='esg-table esg-table--no-mobile esg-section--margin-bottom search-sectiontable')

    sections = []

    # Iterate over each table to extract relevant information
    for table in tables:
        section_info = {}

        # Extract section name from the caption tag
        caption = table.find('caption', class_='offScreen')
        if caption:
            section_info['section_name'] = caption.get_text(strip=True)

        # Extract seat availability
        seats_td = table.find('td', class_='search-seatscell')
        if seats_td:
            seat_info = seats_td.find('span', class_='search-seatsavailabletext')
            section_info['seats'] = seat_info.get_text(strip=True) if seat_info else 'Unavailable'

        # Extract times, locations, and instructors
        rows = table.find_all('tr', class_='search-sectionrow')
        meeting_details = []

        for row in rows:
            meeting_info = {}

            # Extract meeting times
            time_td = row.find('td', class_='search-sectiondaystime')
            if time_td:
                time_divs = time_td.find_all('div')
                meeting_info['times'] = [time_div.get_text(strip=True) for time_div in time_divs]

            # Extract location information
            location_td = row.find('td', class_='search-sectionlocations')
            if location_td:
                location_divs = location_td.find_all('div')
                meeting_info['locations'] = [location_div.get_text(strip=True) for location_div in location_divs]

            # Extract type of event (e.g., LEC, LAB, EXAM)
            if location_td:
                event_type = location_td.find('span', class_='search-meetingtimestext', id=lambda x: x and 'meeting-instructional-method' in x)
                meeting_info['event_type'] = event_type.get_text(strip=True) if event_type else 'Unknown'

            # Append each meeting's details
            meeting_details.append(meeting_info)

        # Extract instructors
        instructor_td = table.find('td', class_='search-sectioninstructormethods')
        instructors = []
        if instructor_td:
            instructor_spans = instructor_td.find_all('span')
            for instructor_span in instructor_spans:
                instructors.append(instructor_span.get_text(strip=True))

        # Add extracted information to section_info
        section_info['meeting_details'] = meeting_details
        section_info['instructors'] = instructors if instructors else ['Instructor TBD']

        # Append the extracted section information to sections list
        sections.append(section_info)

    return sections

# Main function to execute scraping and extraction
def scrape_course_sections(course_code):
    # Scrape the course page using SeleniumBase
    page_source = get_course_page(course_code)

    # If the page source is valid, proceed to extract the course sections
    if page_source:
        sections = extract_course_sections_with_type(page_source)

        # Display extracted section information
        for section in sections:
            print(section, "\n\n\n")

# Execute the function
if __name__ == '__main__':
    course_code = input("Enter course code (e.g., ENGG*3390): ")
    scrape_course_sections(course_code)
