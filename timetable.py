
import win32com.client
from datetime import datetime, timedelta
from langchain_groq import ChatGroq # type: ignore
from langchain_core.prompts import PromptTemplate # type: ignore
import fitz # type: ignore
import sys
import os

from dotenv import load_dotenv
import re
from datetime import datetime



def schedule(content):
    load_dotenv()
    llm = ChatGroq(
        temperature = 0,
        groq_api_key = os.getenv('GROQ_API_KEY'),
        model_name = "llama-3.1-70b-versatile"
    )
    response = llm.invoke(content)
    return response.content
    
def clean_text(text):
    # Ensure the text is encoded in UTF-8 and decoded back to a string
    encoded_text = text.encode('utf-8', errors='ignore')
    utf8_text = encoded_text.decode('utf-8', errors='ignore')
    
    # Optionally replace ligatures or unsupported characters
    utf8_text = utf8_text.replace("\ufb01", "fi").replace("\ufb02", "fl")
    
    # Clean up the text by removing excessive newlines and spaces
    cleaned_text = utf8_text.replace('\n', ' ').replace('\r', '').strip()
    
    return cleaned_text

def get_content_from_pdf(pdf_path):
    # Open the PDF file
    doc = fitz.open(pdf_path)
    text = ""
    # Loop through each page
    for page_num in range(doc.page_count):
        page = doc.load_page(page_num)
        text += page.get_text("text")  # Extract text from the page
    cleaned_pdf_content = clean_text(text)
    return cleaned_pdf_content

def llm_chained_template(content):
    # Get content from the PDF
    # Format the prompt (turn it into a string) by passing the cleaned PDF content to it
    prompt = prompt_extract.format() + "\n" + content
    # print(prompt, "\n")
    # print(type(prompt), "\n")
    # Send to LLM for processing (currently not invoking LLM for debugging purposes)
    result = schedule(prompt)
    return result

prompt_extract = PromptTemplate.from_template(
    """
        Extract all important academic events from this course outline and provide the details for each event in the exact format given below. Do not omit any relevant information. For any missing information (e.g., 'TBA' for location), return 'TBA' or 'N/A' as applicable.

        For each event, provide the following details:

        Event Type: (e.g., Lecture, Lab, Midterm Exam, Final Exam, Assignment, Lab Report).
        Start Date: For recurring events (like lectures, labs), provide the start date.
        End Date: For recurring events (like lectures, labs), provide the end date.
        Date: For one-time events (like exams, assignments), provide the exact date.
        Days: For recurring events (e.g., lectures, labs), specify the days of the week (e.g., Monday, Wednesday, Friday). For one-time events, leave this as 'N/A'.
        Time: Provide the start and end time of the event. If the time is not provided, use 'TBA' or 'N/A'.
        Location: Provide the location of the event. If the location is not provided, use 'TBA'.
        Description: Provide a brief description of the event (e.g., course name, lab number, or exam type).
        Weightage: For events that are graded (e.g., assignments, exams, lab reports), provide the weightage. If not applicable, use 'Null'.

        "event_type": "Lecture",
        "start_date": "2024-09-05",
        "end_date": "2024-12-13",
        "days": ["Monday", "Wednesday", "Friday"],
        "time": "12:30 pm - 1:20 pm",
        "location": "ROZH*102",
        "description": "ENGG*3450 lectures",
        "weightage": "Null"


        "event_type": "Midterm Exam",
        "date": "2024-10-19",
        "time": "12:00 pm - 2:00 pm",
        "location": "TBA",
        "description": "Midterm exam",
        "weightage": "25%"

         "event_type": "Assignment 1",
        "date": "2024-10-07",
        "time": "12:30 pm - 1:20 pm",
        "location": "N/A",
        "description": "Assignment 1",
        "weightage": "7.5%"


        NO PREAMBLE
    """)
import re
from datetime import datetime

def parse_event(event_str):
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
            if date_range[0] != 'TBA':
                event['start_date'] = date_range[0]  # Keep as a string or format as needed
            else:
                event['start_date'] = 'TBA'
            
            if date_range[1] != 'TBA':
                event['end_date'] = date_range[1]  # Keep as a string or format as needed
            else:
                event['end_date'] = 'TBA'
        else:
            if date_range[0] != 'TBA':
                event['date'] = date_range[0]  # Keep as a string or format as needed
            else:
                event['date'] = 'TBA'

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


def parse_all_events(events_str):
    # Split the input string by two newlines to separate events
    event_blocks = events_str.strip().split('\n\n')
    
    # Initialize a list to store all parsed events
    events = []
    
    # Loop through each event block and parse it
    for event_block in event_blocks:
        event = parse_event(event_block)
        events.append(event)
    
    return events

if __name__ == "__main__":
    # Extract the content from the PDF
    pdf_content = get_content_from_pdf("engg-4450-01.pdf")
    
    # Send the extracted content to the LLM template to process and return structured event data
    llm_chained_template_response = llm_chained_template(pdf_content)
    print(llm_chained_template_response)  # Print the LLM response for debugging
    
    # Parse the structured response and extract all events
    event_list = parse_all_events(llm_chained_template_response)
    
    # Print the parsed list of events
    for event in event_list:
        print(event, "\n")


