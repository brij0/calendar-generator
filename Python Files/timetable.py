from datetime import datetime
from math import e
from langchain_groq import ChatGroq
import fitz
import os
from dotenv import load_dotenv
import re
from datetime import datetime
from scrape_course import *

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
        model_name="llama-3.3-70b-versatile"
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
    for page_num in range(doc.page_count - 3):
        page = doc.load_page(page_num)
        text += page.get_text("text")  # Extract text from the page
    
    # Clean up the extracted PDF content
    cleaned_pdf_content = clean_pdf_text(text)
    return cleaned_pdf_content

# ---------------------------------------------------------
# LLM prompt to extract events from the course outline
# ---------------------------------------------------------


def generate_llm_prompt(course_details, student_details):
    prompt_template = """
    Extract only the following types of academic events from the course outline:
    1. For lab sessions:
       - Use dates from course outline
       - Time and day MUST match student's scheduled lab slot from: {student_details}
       - Do not invent or modify lab times
    
    2. Midterm and Final exams
    3. Course-specific assignments and projects
    
    Exclude:
    - Generic recurring lectures
    - University-wide holidays or breaks
    - Administrative dates
    - Make-up classes
    
    4. Format each event:
       Event Type: [LabN/Midterm/FinalExam]
       Date: [YYYY-MM-DD]
       Days: [Use student's scheduled day for the event]
       Time: [Use student's scheduled time for the event]
       Location: [Building,Room]
       Description: [Brief description]
       Weightage: [Number]%

    Course Information:
    {course_details}

    Section Details:
    {student_details}

    Return only events that have confirmed dates and are specific to this course section. Do not return empty events
    """
    
    # Extract section number from student_details
    # return None
    return invoke_llm(prompt_template.format(
        course_details=course_details,
        student_details=student_details
    ))




# ---------------------------------------------------------
# Parse each event and extract details from the LLM response
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
    Student_Details = extract_section_info("HIST", "1250", "01")
    print(Student_Details)
    event_list = process_pdfs_make_event_list("D:/University/All Projects/Time Table project/Sample Course Outlines/HIST_1250.pdf", Student_Details)
    for events in event_list:
        print(f"events in the list are : {events}")