-- Create the courses table

use course_details;
CREATE TABLE courses (
    course_id INT AUTO_INCREMENT PRIMARY KEY,
    section_name VARCHAR(50) NOT NULL,
    seats VARCHAR(50),
    instructor VARCHAR(255)
);

SELECT * FROM courses;
-- Create the events table
CREATE TABLE events (
    event_id INT AUTO_INCREMENT PRIMARY KEY,
    course_id INT NOT NULL,
    event_type VARCHAR(50),
    times VARCHAR(255),
    start_date DATE,
    end_date DATE,
    location VARCHAR(255),
    FOREIGN KEY (course_id) REFERENCES courses(course_id)
);

-- DELETE FROM courses WHERE course_id = '1';
