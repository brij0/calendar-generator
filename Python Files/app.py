from flask import Flask, request, render_template, jsonify
import os
from database import *

app = Flask(__name__, template_folder='D:/University/All Projects/Time Table project/templates')

# Home page to render dropdown menu
@app.route('/')
def index():
    # Fetch distinct course types for the first dropdown
    conn = connect_to_database()
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT course_type FROM courses")
    course_types = [row[0] for row in cursor.fetchall()]
    return render_template('index.html', course_types=course_types)

# API route to fetch course codes based on selected course type
@app.route('/get_course_codes', methods=['POST'])
def get_course_codes():
    course_type = request.json.get('course_type')
    conn = connect_to_database()
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT course_code FROM courses WHERE course_type = %s", (course_type,))
    course_codes = [row[0] for row in cursor.fetchall()]
    return jsonify(course_codes)

# API route to fetch section numbers based on selected course code
@app.route('/get_section_numbers', methods=['POST'])
def get_section_numbers():
    course_code = request.json.get('course_code')
    conn = connect_to_database()
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT section_number FROM courses WHERE course_code = %s", (course_code,))
    section_numbers = [row[0] for row in cursor.fetchall()]
    return jsonify(section_numbers)

# Route to handle the final search and extract course events
@app.route('/search', methods=['POST'])
def search_course():
    # Get the selected values from the form
    courses = []
    for i in range(6):
        course_type = request.form.get(f'course_type_{i}')
        course_code = request.form.get(f'course_code_{i}')
        section_number = request.form.get(f'section_number_{i}')
        if course_type and course_code and section_number:
            courses.append({
                "course_type": course_type,
                "course_code": course_code,
                "section_number": section_number
            })
    # Process and extract events for each selected course
    print(courses)
    event_list = []
    for course in courses:
        events = extract_section_info(course["course_type"], course["course_code"], course["section_number"])
        event_list.extend(events)
    
    # Render the events page with the extracted events
    return render_template('events.html', events=event_list)

if __name__ == '__main__':
    app.run(debug=True)
