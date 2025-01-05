
SELECT * FROM courses;
SELECT * FROM events;
select * from course_events;

use course_details;
CREATE TABLE courses (
    course_id INT AUTO_INCREMENT PRIMARY KEY,
    section_name VARCHAR(50) NOT NULL,
	seats VARCHAR(50),
    instructor VARCHAR(255),
    course_type VARCHAR(20) NOT NULL,
    course_code VARCHAR(20) NOT NULL,
    section_number VARCHAR(20) NOT NULL
);

CREATE TABLE events (
    event_id INT AUTO_INCREMENT PRIMARY KEY,
    course_id INT NOT NULL,
    event_type VARCHAR(50),
    times VARCHAR(255),
    location VARCHAR(255),
    FOREIGN KEY (course_id) REFERENCES courses(course_id)
);


CREATE TABLE course_events (
    event_id INT AUTO_INCREMENT PRIMARY KEY,
    course_id INT NOT NULL,
    event_type VARCHAR(50) NOT NULL,
    event_date DATE,
    start_date DATE,
    end_date DATE,
    days VARCHAR(255),
    time VARCHAR(255),
    location VARCHAR(255),
    description VARCHAR(200),
    weightage VARCHAR(20),
    FOREIGN KEY (course_id) REFERENCES courses(course_id)
);


CREATE TABLE course_dropdown (
    id INT AUTO_INCREMENT PRIMARY KEY,
    course_type VARCHAR(20),
    course_code VARCHAR(20),
    section_number VARCHAR(20)
);