from seleniumbase import SB
from bs4 import BeautifulSoup

# Base URL with course code dynamically appended
BASE_URL = 'https://colleague-ss.uoguelph.ca/Student/Courses/Search?keyword='

def initialize_driver():
    """
    Initialize the SeleniumBase driver with specific settings.
    
    Returns:
        SB: An instance of SeleniumBase driver.
    """
    return SB(uc=True, browser="Chrome", incognito=True)

def get_course_page(course_code):
    """
    Scrape the course page content using SeleniumBase.
    
    Args:
        course_code (str): The course code to be appended to the base URL.
    
    Returns:
        str: The HTML content of the course page.
    """
    url = BASE_URL + course_code
    with initialize_driver() as sb:
        try:
            sb.open(url)
            button_selector = f'button[aria-controls="collapsible-view-available-sections-for-{course_code}-collapseBody"]'
            sb.click(button_selector, timeout=10, delay=0.01)
            sb.wait(3)
            return sb.get_page_source()
        except Exception as e:
            print(f"An error occurred while scraping course sections: {e}")
            return None

def extract_course_sections_with_type(html):
    """
    Extract relevant course details from HTML content.
    
    Args:
        html (str): The HTML content of the course page.
    
    Returns:
        list: A list of dictionaries containing course section details.
    """
    soup = BeautifulSoup(html, 'html.parser')
    tables = soup.find_all('table', class_='esg-table esg-table--no-mobile esg-section--margin-bottom search-sectiontable')
    sections = []

    for table in tables:
        section_info = {}

        caption = table.find('caption', class_='offScreen')
        if caption:
            section_info['section_name'] = caption.get_text(strip=True)

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
        section_info['instructors'] = instructors if instructors else ['TBD']
        sections.append(section_info)

    return sections

def scrape_course_sections(course_code):
    """
    Main function to execute scraping and extraction of course sections.
    
    Args:
        course_code (str): The course code to be scraped.
    """
    page_source = get_course_page(course_code)
    if page_source:
        sections = extract_course_sections_with_type(page_source)
        for section in sections:
            print(section, "\n\n\n")

if __name__ == '__main__':
    course_code = input("Enter course code (e.g., ENGG*3390): ")
    scrape_course_sections(course_code)