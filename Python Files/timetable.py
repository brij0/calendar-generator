import win32com.client
from datetime import datetime, timedelta
from langchain_groq import ChatGroq  # type: ignore
from langchain_core.prompts import PromptTemplate  # type: ignore
import fitz  # type: ignore
import os
from dotenv import load_dotenv
import re
from datetime import datetime
import time

# ---------------------------------------------------------
# Load API key and setup LLM for content processing
# ---------------------------------------------------------
def invoke_llm(content):
    # Load environment variables for API key
    load_dotenv()

    # Initialize the LLM (LLaMA 3.2 model)
    llm = ChatGroq(
        temperature=0,
        groq_api_key=os.getenv('GROQ_API_KEY'),  # API key loaded from environment variable
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
    for page_num in range(doc.page_count):
        page = doc.load_page(page_num)
        text += page.get_text("text")  # Extract text from the page
    
    # Clean up the extracted PDF content
    cleaned_pdf_content = clean_pdf_text(text)
    return cleaned_pdf_content

# ---------------------------------------------------------
# LLM prompt to extract events from the course outline
# ---------------------------------------------------------
def generate_llm_prompt(content):
    # Format the prompt and append the content
    prompt = prompt_extract.format() + "\n" + content

    # Send to LLM for processing and return the result
    result = invoke_llm(prompt)
    return result

# LLM prompt definition for extracting academic events
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
# Function to add events to Outlook Calendar
# ---------------------------------------------------------
def add_event_to_outlook_calendar(subject, start_time, end_time, location=None, recurrence=None, body=None):
    try:
        # Connect to Outlook
        outlook = win32com.client.Dispatch("Outlook.Application")
        calendar = outlook.GetNamespace("MAPI").GetDefaultFolder(9)  # 9 refers to the calendar

        # Create a new appointment item
        appointment = calendar.Items.Add(1)  # 1 refers to a regular appointment

        # Set the details of the appointment
        appointment.Subject = subject
        appointment.Start = start_time
        appointment.End = end_time

        if location:
            appointment.Location = location
        if body:
            appointment.Body = body

        # Handle recurrence if specified
        if recurrence:
            recurrence_pattern = appointment.GetRecurrencePattern()
            recurrence_pattern.RecurrenceType = recurrence.get("type", 1)  # Default to weekly
            recurrence_pattern.Interval = recurrence.get("interval", 1)  # Every X weeks
            recurrence_pattern.PatternStartDate = recurrence.get("start_date", start_time)
            recurrence_pattern.PatternEndDate = recurrence.get("end_date", start_time + timedelta(weeks=12))  # Default 12 weeks

        # Save the appointment
        appointment.Save()
        print(f"Event '{subject}' added to calendar.")
    except Exception as e:
        print(f"Error adding event '{subject}' to calendar: {str(e)}")

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
# Function to handle and add all events to the Outlook Calendar
# ---------------------------------------------------------
def process_and_add_events_to_calendar(events):
    for event in events:
        subject = event.get('description', 'No Title')
        date_str = event.get('date')
        time_str = event.get('time', 'N/A')
        location = event.get('location', 'TBA')
        body = event.get('description')

        # Parse the date and time, skipping if both are 'TBA'/'N/A'
        if date_str and 'TBA' not in date_str:
            if ',' in date_str:
                dates = [d.split(' (')[0].strip() for d in date_str.split(',')]  # Extract individual dates
            else:
                dates = [date_str]
        else:
            dates = []

        # Handle the time string
        if time_str and time_str != 'N/A':
            times = time_str.split(',')
        else:
            times = ['N/A']

        for i, date in enumerate(dates):
            time = times[i] if i < len(times) else 'N/A'
            start_time, end_time = parse_date_and_time(date, time)

            if start_time and end_time:
                add_event_to_outlook_calendar(subject, start_time, end_time, location, None, body)
            else:
                print(f"Skipping event '{subject}' due to missing start or end time.")

# ---------------------------------------------------------
# Function to handle all course outline from the folder
# ---------------------------------------------------------
def process_pdfs_and_add_events_to_calendar(folder_path):
    # Loop through each file in the specified folder
    for file_name in os.listdir(folder_path):
        # Check if the file is a PDF
        if file_name.endswith('.pdf'):
            pdf_path = os.path.join(folder_path, file_name)
            # Extract the content from the PDF
            pdf_content = extract_and_clean_pdf_text(pdf_path)

            # Send the extracted content to the LLM template to process and return structured event data
            llm_chained_template_response = generate_llm_prompt(pdf_content)

            # Parse the structured response and extract all events
            event_list = extract_all_event_details(llm_chained_template_response)

            # Print the parsed list of events for debugging
            for event in event_list:
                print(event, "\n")

            # Add all events to Outlook calendar
            process_and_add_events_to_calendar(event_list)

            print(f"Finished processing {file_name}.\n")


def process_pdfs_make_event_list(pdf_input):
    # Extract the content from the PDF
    pdf_content = extract_and_clean_pdf_text(pdf_input)

    # Send the extracted content to the LLM template to process and return structured event data
    llm_chained_template_response = generate_llm_prompt(pdf_content)
    # Parse the structured response and extract all events
    event_list = extract_all_event_details(llm_chained_template_response)
    return event_list



# ---------------------------------------------------------
# Main function to execute the process
# ---------------------------------------------------------
if __name__ == "__main__":
    folder_path = "Sample Course Outlines" 
    start_time = time.time() 
    event_list = process_pdfs_make_event_list("Sample Course Outlines/ENGG_3640.pdf")
    for event in event_list:
        print(event, "\n")