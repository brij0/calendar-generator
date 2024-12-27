from datetime import datetime
from math import e
from langchain_groq import ChatGroq
import fitz
import os
from dotenv import load_dotenv
import re
from datetime import datetime

from numpy import add
from scrape_course import *
import json

# ---------------------------------------------------------
# Load API key and setup LLM for content processing
# ---------------------------------------------------------
def invoke_llm(content):
    # Load environment variables for API key
    load_dotenv()

    # Initialize the LLM (LLaMA 3.2 model)
    llm = ChatGroq(
        temperature=0,
        groq_api_key=os.getenv('GROQ_API_KEY1'),  # API key loaded from environment variable
        model_name="llama-3.3-70b-specdec"
    )
    
    # Send content to the LLM for processing and return the response
    response = llm.invoke(content)
    return response.content

# ---------------------------------------------------------
# Clean up text from PDF by ensuring proper encoding
# ---------------------------------------------------------
def clean_pdf_text(text):
    # Ensure the text is encoded in UTF-8 and decoded back to a string
    encoded_text = text.encode('utf-8', errors='ignore')
    utf8_text = encoded_text.decode('utf-8', errors='ignore')

    # Optionally replace ligatures or unsupported characters
    utf8_text = utf8_text.replace("\ufb01", "fi").replace("\ufb02", "fl")

    # Clean up the text by removing excessive newlines and spaces
    cleaned_text = utf8_text.replace('\n', ' ').replace('\r', '').strip()

    return cleaned_text

# ---------------------------------------------------------
# Extract text from PDF and clean it
# ---------------------------------------------------------
def extract_and_clean_pdf_text(pdf_path):
    # Open the PDF file
    doc = fitz.open(pdf_path)
    text = ""

    # Loop through each page to extract the text
    for page_num in range(doc.page_count - 4):
        page = doc.load_page(page_num)
        text += page.get_text("text")  # Extract text from the page
    
    # Clean up the extracted PDF content
    cleaned_pdf_content = clean_pdf_text(text)
    return cleaned_pdf_content

# ---------------------------------------------------------
# LLM prompt to extract events from the course outline
# ---------------------------------------------------------


def generate_llm_prompt(course_details, student_details):
    details = student_details.get('section_details')  # Extract section details
    prompt_template = """
    Extract only the following types of academic events from the course outline:
        1. For lab sessions:
        - Use dates from course outline
        - Time and day MUST match student's scheduled lab slot from: {details}
        - Do not invent or modify lab times

    Midterm and Final exams
    Course-specific assignments and projects

    Exclude:

    Generic recurring lectures
    University-wide holidays or breaks
    Administrative dates
    Make-up classes

Format each event as follows (STRICTLY FOLLOW THIS FORMAT WITHOUT EXCEPTION FOR ALL EVENTS. ENSURE NO DETAILS ARE MISSING. If uncertain, use your best judgment to complete missing details based on context):  

- Event Type:  
  Specify the type of event as one of the following: LabN, Midterm, or FinalExam.  

- Date:
  Use the exact date provided in the course outline in the format [YYYY-MM-DD]. For labs marked as "continued," include only the latest date.
  NO OTHER TEXTS ALLOWED.  

- Days:  
  Use the scheduled day for the event based on the student's provided details.  NO OTHER TEXTS.

- Time: 
  Match the exact time of the event as per the course outline or the student's scheduled lab/exam times.  NO OTHER TEXTS.

- Location:
  Include the complete location in the format [Building, Room]. If no location is explicitly stated, note "TBA."  

- Description: 
  Provide a concise description of the event, clearly specifying its purpose (e.g., "Laboratory 1 with report," "Midterm exam covering Weeks 1-5").  

- Weightage:
  Indicate the percentage weightage of the event as a percentage value ONLY (e.g., "8.33%", "25%") check if the explicit weightages are mentioned in the document no other texts.  

Important Notes:
- Every event must include all the above fields. Events with missing details should be completed using contextual judgment or noted explicitly (e.g., "Location: TBA").
- Do not deviate from this format or omit any details under any circumstances.
- Double-check for completeness and accuracy before returning results.

    Course Information:
    {course_details}

    Section Details:
    {details}

    Return only events that have confirmed dates and are specific to this course section. Do not return empty events
    """
    
    # Correctly pass details into the format function
    return invoke_llm(prompt_template.format(
        course_details=course_details,
        details=details
    ))


# ---------------------------------------------------------
# Extract details from an individual event string
# ---------------------------------------------------------
def extract_event_details(event_str):
    event = {}

    # Extract Event Type
    event_type_match = re.search(r"Event Type: (.+)", event_str)
    if event_type_match:
        event['event_type'] = event_type_match.group(1)

    # Extract Date (handles both date ranges and single dates, ignoring 'TBA')
    date_match = re.search(r"Date: (.+)", event_str)
    if date_match:
        date_range = date_match.group(1).split(' - ')
        if len(date_range) > 1:
            event['start_date'] = date_range[0] if date_range[0] != 'TBA' else 'TBA'
            event['end_date'] = date_range[1] if date_range[1] != 'TBA' else 'TBA'
        else:
            event['date'] = date_range[0] if date_range[0] != 'TBA' else 'TBA'

    # Extract Days
    days_match = re.search(r"Days: (.+)", event_str)
    if days_match:
        event['days'] = days_match.group(1).split(', ')

    # Extract Time
    time_match = re.search(r"Time: (.+)", event_str)
    if time_match:
        event['time'] = time_match.group(1)

    # Extract Location
    location_match = re.search(r"Location: (.+)", event_str)
    if location_match:
        event['location'] = location_match.group(1)

    # Extract Description
    description_match = re.search(r"Description: (.+)", event_str)
    if description_match:
        event['description'] = description_match.group(1)

    # Extract Weightage
    weightage_match = re.search(r"Weightage: (.+)", event_str)
    if weightage_match:
        event['weightage'] = weightage_match.group(1)
    
    return event

# ---------------------------------------------------------
# Parse the LLM response to extract multiple events
# ---------------------------------------------------------
def extract_all_event_details(events_str):
    # Split the input string by two newlines to separate events
    event_blocks = events_str.strip().split('\n\n')

    # Initialize a list to store all parsed events
    events = []

    # Loop through each event block and parse it
    for event_block in event_blocks:
        event = extract_event_details(event_block)
        events.append(event)

    return events

# ---------------------------------------------------------
# Helper function to parse date and time strings
# ---------------------------------------------------------
def parse_date_and_time(date_str, time_str):
    try:
        if date_str != 'TBA' and time_str != 'N/A':
            start_time_str, end_time_str = time_str.split(' - ')
            start_time = datetime.strptime(date_str + ' ' + start_time_str.strip(), "%Y-%m-%d %I:%M %p")
            end_time = datetime.strptime(date_str + ' ' + end_time_str.strip(), "%Y-%m-%d %I:%M %p")
            return start_time, end_time
        else:
            return None, None
    except Exception as e:
        print(f"Error parsing date/time: {str(e)}")
        return None, None

# ---------------------------------------------------------
# Main function to extract, parse, and format events
# ---------------------------------------------------------
def process_pdfs_make_event_list(pdf_input, student_details):
    # Extract the content from the PDF
    pdf_content = extract_and_clean_pdf_text(pdf_input)

    # Send the extracted content to the LLM template to process and return structured event data
    llm_chained_template_response = generate_llm_prompt(pdf_content, student_details)

    # Parse the structured response and extract all events
    event_list = extract_all_event_details(llm_chained_template_response)

    return event_list



# ---------------------------------------------------------
# Main function to execute the process
# ---------------------------------------------------------

if __name__ == "__main__":
    # Example student details
    course_type, course_code, section_number = "ENGG", "3450", "0101"
    connection, cursor = connect_to_database()

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
    dict = {key: events}

    for events in dict.values():
        for event in events:
            print(event)
    
    # student_details = extract_section_info("ENGG", "3450", "0101")
    # events = process_pdfs_make_event_list("D:/University/All Projects/Time Table project/Sample Course Outlines/ENGG_3450.pdf", student_details)
    # print(type(events))
    # event_list = []

    # for event in events:
    #     if event != {}:
    #         event_list.append(event)
    #         print(event)

    # insert_events_batch(event_list, student_details['course_id'])

    
    