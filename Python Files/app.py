from flask import Flask, request, render_template, redirect, url_for
import os
from werkzeug.utils import secure_filename
import time
from database import *
from scrape_course import *

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
    course_name = request.form.get('course_name', '').strip().upper()
    course_code = request.form.get('course_code', '').strip().upper()
    section_number = request.form.get('section_number', '').strip().upper()
    
        # Parse the events
    event_list = extract_section_info(course_name, course_code, section_number)
    print(event_list)

        # Add events to Outlook calendar (optional)

    return render_template('events.html', events=event_list)

    # # If file not found, redirect to home page with a message
    # return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
