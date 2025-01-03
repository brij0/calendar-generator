from seleniumbase import SB
from bs4 import BeautifulSoup
from database import *


All_Courses = [
    "ENGG*2010", "ENGG*4010", "ENGG*3020", "ENGG*2120", "ENGG*3010", "ENGG*3070",
    "ENGG*3120", "ENGG*3150", "ENGG*3220", "ENGG*3430", "ENGG*3470", "ENGG*3670",
    "ENGG*3700", "ENGG*4030", "ENGG*4050", "ENGG*4090", "ENGG*4300", "ENGG*4440",
    "ENGG*4470", "ENGG*4510", "ENGG*4580", "ENGG*4760", "ENGG*4810", "ENGG*4820",
    "ENGG*1210", "ENGG*1420", "ENGG*1500", "ENGG*2160", "ENGG*2230", "ENGG*2340",
    "ENGG*2550", "ENGG*2560", "ENGG*3080", "ENGG*3130", "ENGG*3140", "ENGG*3240",
    "ENGG*3250", "ENGG*3260", "ENGG*3280", "ENGG*3340", "ENGG*3570", "ENGG*3650",
    "ENGG*4020", "ENGG*4040", "ENGG*4220", "ENGG*4240", "ENGG*4360", "ENGG*4370",
    "ENGG*4390", "ENGG*4400", "ENGG*4430", "ENGG*4460", "ENGG*4680", "ENGG*4770",
    "ENGG*2100", "ENGG*4380", "ENGG*4110", "ENGG*4130", "ENGG*4160", "ENGG*4170"
    ]

C_Eng_courses =["CHEM*1040", "ENGG*1100", "ENGG*1410", "MATH*1200",
                "ENGG*1420", "MATH*1210", "ENGG*1500", "ENGG*2400", 
                "MATH*2270", "ENGG*2450", "MATH*2130", "ENGG*3240", 
                "ENGG*3410", "ENGG*3450", "ENGG*3100", "PHYS*1010", 
                 "CIS*2520", "ENGG*2410", "ENGG*2100", "ENGG*3380",
                "STAT*2120", "ENGG*4450", "ENGG*3640",  "CIS*3110", 
                 "CIS*3490", "ENGG*3210", "ENGG*4420", "ENGG*4540",
                "ENGG*4550", "ENGG*3390", "ENGG*4000", "COOP*1100", 
                "PHYS*1130", "ENGG*1210",  "CIS*2910", "HIST*1250", 
                "ENGG*3050"]

test = ["ENGG*3390","ENGG*3450","ENGG*3640","ENGG*3700","ENGG*4450","HIST*1250"]

def init_selenium_driver():
    """
    Initialize the SeleniumBase driver with specific settings.
    
    Returns:
        SB: An instance of SeleniumBase driver.
    """
    return SB(uc=True, browser="Chrome", incognito=True)


def extract_course_sections(course_html):
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
                scraped_courses[course] = extract_course_sections(page_source)
            except Exception as e:
                print(f"An error occurred while scraping course sections for {course}: {e}")
                scraped_courses[course] = []  # Add empty list for failed courses
                continue
    
    return scraped_courses



if __name__ == '__main__':
    scraped = scrape_courses(test)
    insert_cleaned_sections(scraped)