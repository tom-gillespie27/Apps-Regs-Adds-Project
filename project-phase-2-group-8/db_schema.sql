DROP DATABASE IF EXISTS `university_integrated`;
CREATE DATABASE `university_integrated`
    DEFAULT CHARACTER SET = 'utf8mb4';
    
USE `university_integrated`;

SET FOREIGN_KEY_CHECKS=1;

-- user
DROP TABLE IF EXISTS `user`;
CREATE TABLE `user`(
    `id`                INT(8) NOT NULL AUTO_INCREMENT PRIMARY KEY,
    `type`              ENUM('sysadmin', 'gs', 'faculty', 'student', 'alum', 'applicant', 'registrar') NOT NULL,
    `email`             VARCHAR(50),
    `username`          VARCHAR(50) UNIQUE,
    `password`          VARCHAR(50),
    `first_name`        VARCHAR(50) NOT NULL,
    `last_name`         VARCHAR(50) NOT NULL,
    `bday`              DATE NOT NULL,
    `street_address`    VARCHAR(50),
    `city`              VARCHAR(50),
    `state`             VARCHAR(2),
    `zip`               VARCHAR(5)
);

-- student_info
DROP TABLE IF EXISTS `student_info`;
CREATE TABLE `student_info`(
    `user_id`                   INT NOT NULL PRIMARY KEY,
    `program`                   ENUM('masters','phd'),
    `advisor_id`                INT,
    `grad_status`               ENUM('pending', 'cleared') NOT NULL DEFAULT 'pending',
    `thesis_passed`             TINYINT(1) NOT NULL DEFAULT 0,
    `form_approved`             TINYINT(1) NOT NULL DEFAULT 0,
    `advising_form_approved`    TINYINT(1) NOT NULL DEFAULT 0,
    `grad_semester`             ENUM('fall', 'spring') NOT NULL,
    `grad_year`                 YEAR NOT NULL DEFAULT (YEAR(CURDATE()) + 2),
    `admit_year`                YEAR NOT NULL DEFAULT (YEAR(CURDATE())),
    FOREIGN KEY                 (`user_id`) REFERENCES `user`(`id`)
                                ON DELETE CASCADE,
    FOREIGN KEY                 (`advisor_id`) REFERENCES `user`(`id`)
                                ON DELETE SET NULL
);

-- faculty_info
DROP TABLE IF EXISTS `faculty_info`;
CREATE TABLE `faculty_info` (
    `user_id`               INT NOT NULL PRIMARY KEY,
    `department`            ENUM('CSCI','ECE','MATH') NOT NULL,
    `is_advisor`            TINYINT(1) NOT NULL DEFAULT 0,
    `is_reviewer`           TINYINT(1) NOT NULL DEFAULT 0,
    `is_instructor`         TINYINT(1) NOT NULL DEFAULT 0,
    `is_admissions_chair`   TINYINT(1) NOT NULL DEFAULT 0,
    FOREIGN KEY             (`user_id`) REFERENCES `user`(`id`)
                            ON DELETE CASCADE
);

--alumni info 
DROP TABLE IF EXISTS `alumni_info`;
CREATE TABLE `alumni_info`(
    `user_id`           INT NOT NULL PRIMARY KEY,
    `program`           ENUM('masters','phd'),
    `grad_semester`     ENUM('fall', 'spring') NOT NULL,
    `grad_year`         YEAR NOT NULL DEFAULT (YEAR(CURDATE())),
    FOREIGN KEY         (`user_id`) REFERENCES `user`(`id`)
                        ON DELETE CASCADE
);

-- degree_requirements
DROP TABLE IF EXISTS `degree_requirements`;
CREATE TABLE `degree_requirements`(
    `program`           ENUM('masters', 'phd') NOT NULL,
    `requirement`       ENUM('min_gpa', 'min_credit_hours', 'most_non_cs_courses', 'min_cs_credit_hours', 'most_below_b_grades', 'thesis_passed') NOT NULL,
    `value`             FLOAT(4,2) NOT NULL,
    PRIMARY KEY         (`program`, `requirement`)
);

-- course
DROP TABLE IF EXISTS `course`;
CREATE TABLE `course`(
    `id`                INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    `department`        ENUM('CSCI','ECE','MATH') NOT NULL,
    `course_num`        SMALLINT(4) NOT NULL,
    `title`             VARCHAR(50) NOT NULL,
    `credits`           TINYINT(1) NOT NULL,
    `required_masters`  TINYINT(1) NOT NULL,
    UNIQUE              (`department`, `course_num`)
);

-- course_prereq
DROP TABLE IF EXISTS `course_prereq`;
CREATE TABLE `course_prereq`(
    `course_id`     INT NOT NULL,
    `prereq_id`     INT NOT NULL,
    PRIMARY KEY     (`course_id`, `prereq_id`),
    FOREIGN KEY     (`course_id`) REFERENCES `course`(`id`)
                    ON DELETE CASCADE,
    FOREIGN KEY     (`prereq_id`) REFERENCES `course`(`id`)
                    ON DELETE CASCADE
);

-- sections
DROP TABLE IF EXISTS `sections`;
CREATE TABLE `sections` (
    `course_id`         INT NOT NULL,
    `csem`              ENUM('fall', 'spring') NOT NULL,
    `cyear`             YEAR NOT NULL DEFAULT (YEAR(CURDATE())),
    `day_of_week`       ENUM('M', 'T', 'W', 'R', 'F') NOT NULL,
    `class_time`        VARCHAR(50) NOT NULL,
    `room`              VARCHAR(50) NOT NULL,
    `room_capacity`     SMALLINT(4) NOT NULL,
    `fid`               INT NOT NULL,
    PRIMARY KEY         (`course_id`, `csem`, `cyear`),
    FOREIGN KEY         (`course_id`) REFERENCES `course`(`id`)
                        ON DELETE CASCADE,
    FOREIGN KEY         (`fid`) REFERENCES `faculty_info`(`user_id`)
                        ON DELETE CASCADE
); 

-- student_courses_planned
DROP TABLE IF EXISTS `student_courses_planned`;
CREATE TABLE `student_courses_planned`(
    `user_id`       INT NOT NULL AUTO_INCREMENT,
    `course_id`     INT NOT NULL,
    `form`          ENUM('advising', 'form1') NOT NULL DEFAULT 'form1',
    PRIMARY KEY     (`user_id`, `course_id`, `form`),
    FOREIGN KEY     (`user_id`) REFERENCES `user`(`id`)
                    ON DELETE CASCADE,
    FOREIGN KEY     (`course_id`) REFERENCES `course`(`id`)
                    ON DELETE CASCADE
);

-- student_courses
DROP TABLE IF EXISTS `student_courses`;
CREATE TABLE `student_courses`(
    `user_id`       INT NOT NULL AUTO_INCREMENT,
    `course_id`     INT NOT NULL,
    `semester`      ENUM('fall', 'spring') NOT NULL,
    `year`          YEAR NOT NULL DEFAULT (YEAR(CURDATE())),
    `grade`         ENUM('A', 'A-', 'B+', 'B', 'B-', 'C+', 'C', 'F', 'IP') NOT NULL DEFAULT 'IP',
    PRIMARY KEY     (`user_id`, `course_id`, `semester`, `year`),
    FOREIGN KEY     (`user_id`) REFERENCES `user`(`id`)
                    ON DELETE CASCADE,
    FOREIGN KEY     (`course_id`) REFERENCES `course`(`id`)
                    ON DELETE CASCADE,
    FOREIGN KEY     (`course_id`, `semester`, `year`) REFERENCES `sections`(`course_id`, `csem`, `cyear`)
                    ON DELETE CASCADE
);
-- alumni_chat_messages
DROP TABLE IF EXISTS `alumni_chat_messages`;
CREATE TABLE `alumni_chat_messages`(
    `user_id`       INT NOT NULL,
    `message`       VARCHAR(255) NOT NULL,
    `timestamp`     TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY     (`user_id`) REFERENCES `user`(`id`)
                    ON DELETE CASCADE,
    PRIMARY KEY     (`user_id`, `timestamp`)
);
-- **********************************************************************************************************
-- APPLICATION SCHEMA 
DROP TABLE IF EXISTS applicant;
CREATE TABLE applicant (   
   university_id INT(8) NOT NULL PRIMARY KEY,
   ssn INT(9) NOT NULL,
   appStatus ENUM('Pending', 'Incomplete', 'Complete', 'Under Review', 'Admit', 'Admit With Aid', 'Reject', 'Accepted', 'Matriculated') NOT NULL DEFAULT 'Pending',
   mail_transcript VARCHAR(32),
   FOREIGN KEY (university_id) REFERENCES user(id) ON DELETE CASCADE
);

DROP TABLE IF EXISTS applicationForm;
CREATE TABLE applicationForm (
   university_id INT(8) NOT NULL,
   degreeSeeking ENUM('masters', 'phd') NOT NULL,
   MScheck VARCHAR(32),
   MSmajor VARCHAR(32),
   MSyear INT(4),
   MSuniversity VARCHAR(32),
   MSgpa decimal(3,2),
   BAcheck VARCHAR(32) NOT NULL,
   BAmajor VARCHAR(32) NOT NULL,
   BAyear INT(4) NOT NULL,
   BAuniversity VARCHAR(32) NOT NULL,
   BAgpa decimal(3,2),
   GREverbal INT(4),
   GREquantitative INT(4),
   GREyear INT(4),
   GREadvancedScore INT(4),
   GREadvancedSubject VARCHAR(32),
   TOEFLscore INT(4),
   TOEFLdate VARCHAR(32),
   priorWork VARCHAR(300) NOT NULL,
   startDate VARCHAR(32) NOT NULL,
   transcriptStatus VARCHAR(32),
   r1status VARCHAR(32) NOT NULL,
   r1writer VARCHAR(32) NOT NULL,
   r1email VARCHAR(32) NOT NULL,
   r1title VARCHAR(32) NOT NULL,
   r1affiliation VARCHAR(32) NOT NULL,
   r1letter VARCHAR(500),
   r2status VARCHAR(32) NOT NULL,
   r2writer VARCHAR(32) NOT NULL,
   r2email VARCHAR(32) NOT NULL,
   r2title VARCHAR(32) NOT NULL,
   r2affiliation VARCHAR(32) NOT NULL,
   r2letter VARCHAR(500),
   r3status VARCHAR(32) NOT NULL,
   r3writer VARCHAR(32) NOT NULL,
   r3email VARCHAR(32) NOT NULL,
   r3title VARCHAR(32) NOT NULL,
   r3affiliation VARCHAR(32) NOT NULL,
   r3letter VARCHAR(500),
   date_submitted DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
   recommended_advisor INT,
   transcript BLOB,
   PRIMARY KEY (startDate, university_id),
   FOREIGN KEY (university_id) REFERENCES applicant(university_id) ON DELETE CASCADE,
   FOREIGN KEY (recommended_advisor) REFERENCES faculty_info(user_id) ON DELETE SET NULL
);

DROP TABLE IF EXISTS reviewForm;
CREATE TABLE reviewForm (
   university_id INT(8) NOT NULL,
   reviewer INT(8) NOT NULL,
   r1rating INT(1) NOT NULL,
   r1generic VARCHAR(32) NOT NULL,
   r1credible VARCHAR(32) NOT NULL,
   r1from VARCHAR(32) NOT NULL,
   r2rating INT(1),
   r2generic VARCHAR(32),
   r2credible VARCHAR(32),
   r2from VARCHAR(32),
   r3rating INT(1),
   r3generic VARCHAR(32),
   r3credible VARCHAR(32),
   r3from VARCHAR(32),
   GASrating ENUM('Reject', 'Borderline Reject', 'Borderline Admit', 'Admit Without Aid', 'Admit With Aid') NOT NULL,
   deficiencies VARCHAR(40),
   rejectReason VARCHAR(1),
   thoughts VARCHAR(40),
   semesterApplied VARCHAR(32) NOT NULL,
   PRIMARY KEY(university_id, reviewer),
   Foreign Key (university_id) REFERENCES applicant(university_id) ON DELETE CASCADE,
   Foreign Key (reviewer) REFERENCES user(id) ON DELETE CASCADE
);

DROP TABLE IF EXISTS transcript;
CREATE TABLE transcript (
    trans_id INTEGER,
    file_name TEXT,
    mimetype TEXT,
    file_data BLOB,

    PRIMARY KEY (trans_id),
    Foreign Key (trans_id) REFERENCES applicant(university_id) ON DELETE CASCADE
);



