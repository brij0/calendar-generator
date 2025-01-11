from seleniumbase import SB
from bs4 import BeautifulSoup
from database import *


winter_2025_courses = ['ACCT*1220', 'ACCT*1240', 'ACCT*2230', 'ACCT*4230', 'BIOCH*2580', 'BIOM*2000', 
           'CHEM*1050', 'CIS*1500', 'CIS*2500', 'CIS*2750', 'CIS*2910', 'CIS*3110', 
           'CIS*3490', 'CIS*3750', 'CIS*4650', 'COOP*1100', 'ECON*1050', 'ECON*1100', 
           'ECON*2100', 'ECON*2310', 'ECON*2410', 'ECON*2740', 'ECON*2770', 'ECON*3100', 
           'ECON*3400', 'ECON*3530', 'ECON*3580', 'ECON*3610', 'ECON*3620', 'ECON*3710', 
           'ECON*3740', 'ECON*3760', 'ECON*3810', 'ECON*4400', 'ECON*4700', 'ECON*4720', 
           'ECON*4760', 'ECON*4780', 'ECON*4800', 'ECON*4810', 'ECON*4900', 'ECON*4910', 
           'ECON*4930', 'ENGG*1210', 'ENGG*1420', 'ENGG*1500', 'ENGG*2100', 'ENGG*2120', 
           'ENGG*2230', 'ENGG*2330', 'ENGG*2340', 'ENGG*2450', 'ENGG*2560', 'ENGG*3100', 
           'ENGG*3170', 'ENGG*3220', 'ENGG*3340', 'ENGG*3370', 'ENGG*3380', 'ENGG*3420', 
           'ENGG*3430', 'ENGG*3440', 'ENGG*3450', 'ENGG*3470', 'ENGG*4120', 'ENGG*4160', 
           'ENGG*4180', 'ENGG*4450', 'ENGG*4470', 'ENGG*4550', 'FARE*1400', 'FARE*2410', 
           'FARE*3310', 'FARE*4000', 'FARE*4220', 'FARE*4240', 'FIN*2000', 'FIN*3000', 
           'FIN*3100', 'FIN*3400', 'FIN*3500', 'FIN*3900', 'FIN*4000', 'FIN*4100', 
           'FIN*4200', 'FIN*4900', 'HIST*1250', 'HROB*2090', 'HROB*2290', 'MATH*1030', 
           'MATH*1160', 'MATH*1210', 'MATH*2130', 'MCS*1000', 'MCS*2000', 'MCS*2020', 
           'MCS*3040', 'MGMT*1200', 'MGMT*2190', 'MGMT*4000', 'MGMT*4040', 'MGMT*4200', 
           'MICR*2420', 'PATH*3610', 'PHYS*1010']

Arts_courses = [
    "ARTH*3210", "ARTH*4320", "CLAS*2000", "CLAS*2220", "CLAS*2360", "CLAS*3030",
    "CLAS*3080", "CLAS*3150", "CLAS*4400", "CREA*1010", "CRWR*2000", "CRWR*2400",
    "CRWR*3400", "CRWR*3500", "CRWR*4100", "ENGL*1080", "ENGL*2080", "ENGL*2130",
    "ENGL*2360", "ENGL*2740", "ENGL*3570", "ENGL*3960", "ENGL*4250", "ENGL*4500",
    "ENGL*6691", "ENGL*6811", "EURO*4600", "EURO*6010", "EURO*6020", "EURO*6070",
    "FREN*1200", "FREN*1300", "FREN*2020", "FREN*2500", "FREN*3140", "FREN*3520",
    "FREN*4020", "FREN*6020", "GERM*1110", "GERM*3020", "GERM*3150", "GERM*3470",
    "HIST*1050", "HIST*1150", "HIST*2090", "HIST*2120", "HIST*2200", "HIST*2250",
    "HIST*2300", "HIST*2340", "HIST*2850", "HIST*3130", "HIST*3360", "HIST*3480",
    "HIST*3490", "HIST*3620", "HIST*3750", "HIST*3840", "HIST*4200", "HIST*4450",
    "HIST*4580", "HUMN*3000", "HUMN*3020", "HUMN*3470", "ITAL*1060", "ITAL*1070",
    "ITAL*3060", "LAT*1110", "LING*1000", "LING*2400", "LING*3010", "MUSC*2420",
    "MUSC*3420", "MUSC*3490", "MUSC*4450", "SART*1060", "SART*2090", "SART*2200",
    "SART*2460", "SART*2610", "SART*3660", "SART*3750", "SART*4410", "SART*4700",
    "SART*4900", "SPAN*1110", "SPAN*1500", "SPAN*2010", "THST*1190", "THST*2050",
    "THST*3140", "THST*3150", "THST*3170", "THST*4270", "THST*4280" ]



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
    sections = []
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
    engg = ['ENGG*3130', 'ENGG*3210', 'ENGG*3410', 'ENGG*3490', 'ENGG*4430', 'ENGG*4490', 'ENGG*4510', 'ENGG*4540']
    scraped = scrape_courses(engg)
    insert_cleaned_sections(scraped)




