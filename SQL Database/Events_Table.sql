-- Create the courses table

SELECT * FROM courses;
SELECT * FROM events;

SET FOREIGN_KEY_CHECKS = 0;
-- truncate table courses;
-- truncate table events;
-- SET SQL_SAFE_UPDATES = 0;



use course_details;
CREATE TABLE courses (
    course_id INT AUTO_INCREMENT PRIMARY KEY,
    course_type VARCHAR(20) NOT NULL,
    course_code VARCHAR(20) NOT NULL,
    section_number VARCHAR(20) NOT NULL,
    section_name VARCHAR(50) NOT NULL,
    seats VARCHAR(50),
    instructor VARCHAR(255)
);

CREATE TABLE events (
    event_id INT AUTO_INCREMENT PRIMARY KEY,
    course_id INT NOT NULL,
    event_type VARCHAR(50),
    times VARCHAR(255),
    location VARCHAR(255),
    FOREIGN KEY (course_id) REFERENCES courses(course_id)
);

