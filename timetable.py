
import win32com.client
from datetime import datetime, timedelta
from langchain_groq import ChatGroq # type: ignore
from langchain_core.prompts import PromptTemplate # type: ignore
import pdfplumber # type: ignore
import fitz # type: ignore
import sys
import os
sys.stdout.reconfigure(encoding='utf-8')
from dotenv import load_dotenv


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
       Extract structured information from this document for adding events to a calendar. Format the output for each event as a Python dictionary with the following fields:

event_type: The type of the event (e.g., 'Lecture', 'Lab', 'Midterm Exam', 'Final Exam', 'Deadline').
is_recurring: Provide 1 if the event is recurring, otherwise 0 if it’s a one-time event.
date: For one-time events, provide the exact date. For recurring events, provide the start date and end date separately as start_date and end_date.
time: Provide the start and end time of the event.
location: The location of the event. If the event is a quiz or in-class activity, use the same location as the lecture unless specified otherwise.
description: A brief description of the event (e.g., course name or type of exam).
weightage: For events like exams, labs, or assignments, include the weightage (if applicable). If not applicable, return None.
For recurring events, also provide the recurrence pattern (e.g., 'Every Monday'). Format the response as a Python dictionary for each event without unnecessary details or explanations.
        NO PREAMBLE
    """)

def add_class_to_calendar(subject, start_time, end_time, location=None, recurrence=None, body=None):
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

    # Set recurrence pattern if required (for weekly classes)
    if recurrence:
        recurrence_pattern = appointment.GetRecurrencePattern()
        recurrence_pattern.RecurrenceType = recurrence["type"]
        recurrence_pattern.Interval = recurrence.get("interval", 1)  # Every X weeks
        recurrence_pattern.PatternStartDate = recurrence["start_date"]
        recurrence_pattern.PatternEndDate = recurrence["end_date"]

    # Save the appointment
    appointment.Save()
    print(f"Class '{subject}' added to calendar.")

if __name__ == "__main__":
    pdf_content = get_content_from_pdf("Course Outline_ENGG3700_F24.pdf")
    llm_chained_template_response = llm_chained_template(pdf_content)
    print(llm_chained_template_response)
    print(type(llm_chained_template_response))


