
import win32com.client
from datetime import datetime, timedelta
from langchain_groq import ChatGroq # type: ignore
from langchain_core.prompts import PromptTemplate # type: ignore
import pdfplumber # type: ignore
import fitz # type: ignore
import sys
sys.stdout.reconfigure(encoding='utf-8')


def schedule(content):
    llm = ChatGroq(
        temperature = 0,
        groq_api_key = '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',
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
        Extract all important dates, times, associated activities, and the weightage of components from this document. Focus on identifying the following:

        Lecture schedules (days, start and end times, location).
        Laboratory schedules (days, start and end times, location).
        Important deadlines for assignments, labs, or reports, including their weightage.
        Exam dates (midterms and final exams), with times, locations, and weightage.
        Any other key academic events such as study breaks or review sessions.
        For each entry, provide:

        The date,
        The time,
        A brief description of the event,
        And, if applicable, the weightage of the component (e.g., assignments, labs, exams)."
        Example Input:
        "Lectures: MonWedFri 12:30pm-1:20pm in ROZH*102 (9/5 to 12/13)"
        "Midterm Exam: Oct 19, 12:00 PM - 2:00 PM (25%)"
        "Final Exam: Dec 2, Mon 11:30am-1:30pm (35%)"
        "Laboratories '25%' of total grade, assignments 15%"
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
    pdf_content = get_content_from_pdf("w24.hist1250.outline.final.pdf")
    llm_chained_template_response = llm_chained_template(pdf_content)
    print(llm_chained_template_response)


