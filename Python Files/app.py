from flask import Flask, request, render_template, jsonify
import os
from database import *

app = Flask(__name__, template_folder='D:/University/All Projects/Time Table project/templates')

@app.route('/')
def index():
    connection, cursor = connect_to_database()
    cursor.execute("SELECT DISTINCT course_type FROM courses")
    course_types = [row[0] for row in cursor.fetchall()]
    return render_template('index.html', course_types=course_types)

@app.route('/get_course_codes', methods=['POST'])
def get_course_codes():
    course_type = request.json.get('course_type')
    connection, cursor = connect_to_database()
    cursor.execute("SELECT DISTINCT course_code FROM courses WHERE course_type = %s", (course_type,))
    course_codes = [row[0] for row in cursor.fetchall()]
    return jsonify(course_codes)

@app.route('/get_section_numbers', methods=['POST'])
def get_section_numbers():
    course_code = request.json.get('course_code')
    connection, cursor = connect_to_database()
    cursor.execute("SELECT DISTINCT section_number FROM courses WHERE course_code = %s", (course_code,))
    section_numbers = [row[0] for row in cursor.fetchall()]
    return jsonify(section_numbers)

@app.route('/search', methods=['POST'])
def search_course():
    all_events = {}
    
    # Get all form data
    form_data = request.form
    
    # Iterate through form data to find course selections
    i = 0
    while True:
        course_type = form_data.get(f'course_type_{i}')
        course_code = form_data.get(f'course_code_{i}')
        section_number = form_data.get(f'section_number_{i}')
        
        # Break if we don't find any more course entries
        if not any([course_type, course_code, section_number]):
            break
            
        # If we have all three values for this course, get its events
        if all([course_type, course_code, section_number]):
            events = extract_section_info(course_type, course_code, section_number)
            all_events[course_code] = events
            
        i += 1
    
    return render_template('events.html', events=all_events)

if __name__ == '__main__':
    app.run(debug=True)