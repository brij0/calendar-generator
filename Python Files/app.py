from flask import Flask, request, render_template, redirect, url_for
import os
from werkzeug.utils import secure_filename
import time

# Import your existing functions
from timetable import *

app=Flask(__name__,template_folder='D:/University/All Projects/Time Table project/templates')

# Configuration for file uploads
UPLOAD_FOLDER = 'D:/University/All Projects/Time Table project/Sample Course Outlines'  # Folder containing pre-existing course outline PDFs
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Home page to enter course name
@app.route('/')
def index():
    return render_template('index.html')

# Route to handle the course name input and search for the corresponding file
@app.route('/search', methods=['POST'])
def search_course():
    # Get the course name from the form
    course_name = request.form.get('course_name', '').strip().lower()

    if not course_name:
        return redirect(url_for('index'))

    # Search for the PDF file that matches the course name
    file_name = None
    for file in os.listdir(app.config['UPLOAD_FOLDER']):
        if file.lower().startswith(course_name) and file.endswith('.pdf'):
            file_name = file
            break
    
    student_details = """
        Section Name: ENGG*3390*0201
        Instructors: Aboagye, S

        Meeting Details:
        1. Event Type: Lecture (LEC)
        - Days: Tuesday and Thursday
        - Times: 10:00 AM - 11:20 AM
        - Dates: 9/5/2024 - 12/13/2024
        - Location: Guelph, MCKN120

        2. Event Type: Labs
        - Days: Friday
        - Times: 11:30 AM - 1:20 PM
        - Dates: 9/5/2024 - 12/13/2024
        - Location: Guelph, THRN2307

        3. Event Type: Exam
        - Day: Wednesday
        - Times: 7:00 PM - 9:00 PM
        - Dates: 12/4/2024
        - Location: Guelph, ROZH101  
    """

    if file_name:
        # File found, process the PDF
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], file_name)

        # Parse the events
        event_list = process_pdfs_make_event_list(file_path, student_details)

        # Add events to Outlook calendar (optional)

        return render_template('events.html', events=event_list)

    # If file not found, redirect to home page with a message
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
