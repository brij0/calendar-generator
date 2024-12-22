-- Create the courses table

use course_details;
CREATE TABLE courses (
    course_id INT AUTO_INCREMENT PRIMARY KEY,
    section_name VARCHAR(50) NOT NULL,
    seats VARCHAR(50),
    instructor VARCHAR(255)
);

SELECT * FROM courses;
SELECT * FROM events;


-- truncate table courses;
-- truncate table events;


-- Create the events table
CREATE TABLE events (
    event_id INT AUTO_INCREMENT PRIMARY KEY,
    course_id INT NOT NULL,
    event_type VARCHAR(50),
    times VARCHAR(255),
    location VARCHAR(255),
    FOREIGN KEY (course_id) REFERENCES courses(course_id)
);

