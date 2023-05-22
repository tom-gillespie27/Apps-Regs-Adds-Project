USE `university_integrated`;
SET FOREIGN_KEY_CHECKS=1;

-- -----------------------------------------------------
-- Remove existing data
-- -----------------------------------------------------
DELETE FROM `user`;
ALTER TABLE `user` AUTO_INCREMENT = 1;
DELETE FROM `applicant`;
DELETE FROM `applicationForm`;
DELETE FROM `reviewForm`;
DELETE FROM `student_info`;
DELETE FROM `alumni_chat_messages`;
DELETE FROM `alumni_info`;
DELETE FROM `faculty_info`;
DELETE FROM `course_prereq`;
DELETE FROM `student_courses`;
DELETE FROM `student_courses_planned`;
DELETE FROM `sections`;
DELETE FROM `course`;
ALTER TABLE `course` AUTO_INCREMENT = 1;
DELETE FROM `degree_requirements`;

-- -----------------------------------------------------
-- Table `user`
-- -----------------------------------------------------
INSERT INTO `user` (`type`, `email`, `username`, `password`, `first_name`, `last_name`, `street_address`, `city`, `state`, `zip`, `bday`) VALUES ('student', 'ringostarr@gmail.com', 'ringo', '123', 'Ringo', 'Starr', '123 Main St', 'New York', 'NY', '10001', '2000-01-01');
INSERT INTO `user` (`type`, `email`, `username`, `password`, `first_name`, `last_name`, `street_address`, `city`, `state`, `zip`, `bday`) VALUES ('gs', 'erichcast@gmail.com', 'erich', '123', 'Erich', 'Cast', '123 Main St', 'New York', 'NY', '10001', '2000-01-01');
INSERT INTO `user` (`type`, `email`, `username`, `password`, `first_name`, `last_name`, `street_address`, `city`, `state`, `zip`, `bday`) VALUES ('faculty', 'narahari@gwu.edu', 'narahari', '123', 'Bhagi', 'Narahari', '123 Main St', 'New York', 'NY', '10001', '2000-01-01');
INSERT INTO `user` (`type`, `email`, `username`, `password`, `first_name`, `last_name`, `street_address`, `city`, `state`, `zip`, `bday`) VALUES ('faculty', 'parmer@gwu.edu', 'parmer', '123', 'Gabe', 'Parmer', '123 Main St', 'New York', 'NY', '10001', '2000-01-01');
INSERT INTO `user` (`type`, `email`, `username`, `password`, `first_name`, `last_name`, `street_address`, `city`, `state`, `zip`, `bday`) VALUES ('sysadmin', 'jrt@gwu.edu', 'james', '123', 'James', 'Taylor', '123 Main St', 'New York', 'NY', '10001', '2000-01-01');
INSERT INTO `user` (`type`, `email`, `username`, `password`, `first_name`, `last_name`, `street_address`, `city`, `state`, `zip`, `bday`) VALUES ('registrar', 'registrar@gwu.edu', 'registrar', '123', 'Registrar', 'Office', '123 Main St', 'New York', 'NY', '10001', '2000-01-01');
INSERT INTO `user` (`type`, `email`, `username`, `password`, `first_name`, `last_name`, `street_address`, `city`, `state`, `zip`, `bday`) VALUES ('faculty', 'choi@gwu.edu', 'choi', '123', 'Hyeong-Ah', 'Choi', '123 Main St', 'New York', 'NY', '10001', '2000-01-01');
INSERT INTO `user` (`type`, `email`, `username`, `password`, `first_name`, `last_name`, `street_address`, `city`, `state`, `zip`, `bday`) VALUES ('faculty', 'wood@gwu.edu', 'wood', '123', 'Tim', 'Wood', '123 Main St', 'New York', 'NY', '10001', '2000-01-01');
INSERT INTO `user` (`type`, `email`, `username`, `password`, `first_name`, `last_name`, `street_address`, `city`, `state`, `zip`, `bday`) VALUES ('faculty', 'heller@gwu.edu', 'heller', '123', 'Shelly', 'Heller', '123 Main St', 'New York', 'NY', '10001', '2000-01-01');
INSERT INTO `user` (`id`, `type`, `email`, `username`, `password`, `first_name`, `last_name`, `street_address`, `city`, `state`, `zip`, `bday`) VALUES (88888888, 'student', 'billieholiday@gmail.com', 'billie', '123', 'Billie', 'Holiday', '123 Main St', 'New York', 'NY', '10001', '2000-01-01');
INSERT INTO `user` (`id`, `type`, `email`, `username`, `password`, `first_name`, `last_name`, `street_address`, `city`, `state`, `zip`, `bday`) VALUES (99999999, 'student', 'dianakroall@gmail.com', 'diana', '123', 'Diana', 'Krall', '123 Main St', 'New York', 'NY', '10001', '2000-01-01');
INSERT INTO `user` (`id`, `type`, `email`, `username`, `password`, `first_name`, `last_name`, `street_address`, `city`, `state`, `zip`, `bday`) VALUES (55555555, 'student', 'paulmccartney@gmail.com', 'paul', '123', 'Paul', 'McCartney', '123 Main St', 'New York', 'NY', '10001', '2000-01-01');
INSERT INTO `user` (`id`, `type`, `email`, `username`, `password`, `first_name`, `last_name`, `street_address`, `city`, `state`, `zip`, `bday`) VALUES (66666666, 'student', 'georgeharrison@gmail.com', 'george', '123', 'George', 'Harrison', '123 Main St', 'New York', 'NY', '10001', '2000-01-01');
INSERT INTO `user` (`id`, `type`, `email`, `username`, `password`, `first_name`, `last_name`, `street_address`, `city`, `state`, `zip`, `bday`) VALUES (77777777, 'alum', 'ericclapton@gmail.com', 'eric', '123', 'Eric', 'Clapton', '123 Main St', 'New York', 'NY', '10001', '2000-01-01');
INSERT INTO `user` (`id`, `type`, `email`, `username`, `password`, `first_name`, `last_name`, `street_address`, `city`, `state`, `zip`, `bday`) VALUES (12312312, 'applicant', 'johnlennon@gmail.com', 'john', '123', 'John', 'Lennon', '123 Main St', 'New York', 'NY', '10001', '2000-01-01');
INSERT INTO `user` (`id`, `type`, `email`, `username`, `password`, `first_name`, `last_name`, `street_address`, `city`, `state`, `zip`, `bday`) VALUES (32132132, 'applicant', 'normanchapman@gmail.com', 'norman', '123', 'Norman', 'Chapman', '123 Main St', 'New York', 'NY', '10001', '2000-01-01');

-- -----------------------------------------------------
-- Table `applicant`
-- -----------------------------------------------------
INSERT INTO `applicant` (`university_id`, `ssn`, `appStatus`) VALUES (12312312, '111111111', 'Complete');
INSERT INTO `applicant` (`university_id`, `ssn`) VALUES (32132132, '222111111');

-- -----------------------------------------------------
-- Table `applicationForm`
-- -----------------------------------------------------
INSERT INTO `applicationForm` ( `university_id`, `degreeSeeking`, `BAcheck`, `BAmajor`, `BAyear`, `BAuniversity`, `BAgpa`, `priorWork`, `startDate`, `transcriptStatus`, `r1status`, `r1writer`, `r1email`, `r1title`, `r1affiliation`, `r1letter`, `r2status`, `r2writer`, `r2email`, `r2title`, `r2affiliation`, `r2letter`, `r3status`, `r3writer`, `r3email`, `r3title`, `r3affiliation`, `r3letter`) VALUES (12312312, 'masters', '1', 'Computer Science', 2023, 'ABC University', 4.00, 'Server at Planta', 'Fall 2023', 'Transcript Received', 'Received', 'John Doe', 'johndoe@example.com', 'Professor', 'ABC University', 'Dear Admissions Committee, I am pleased to recommend John Lennon for admission to your prestigious music program. As a former bandmate and collaborator, I have no doubt that John\'s unique musical talents and artistic vision will make him a valuable addition to your community.', 'Received', 'Jane Doe', 'janedoe@example.com', 'Manager', 'Planta', 'Dear Admissions Committee, I highly recommend John Lennon for admission to your prestigious music program. John is an exceptionally talented musician, with a unique style and a passion for creating music that truly moves people.', 'Received', 'Joe Biden', 'potus@example.com', 'POTUS', 'US Government', 'Dear Admissions Committee, I am writing to recommend John Lennon for admission to your music program. John is a talented musician and songwriter with a unique sound and style, and I believe that he would make a valuable contribution to your program.');

-- -----------------------------------------------------
-- Table `student_info`
-- -----------------------------------------------------
INSERT INTO `student_info` (`user_id`, `program`, `advisor_id`, `grad_semester`, `grad_year`) VALUES (55555555, 'masters', 3, 'fall', '2023');
INSERT INTO `student_info` (`user_id`, `program`, `advisor_id`, `grad_semester`, `grad_year`) VALUES (66666666, 'masters', 4, 'fall', '2023');
INSERT INTO `student_info` (`user_id`, `program`, `advisor_id`, `grad_semester`, `grad_year`) VALUES (1, 'phd', 4, 'fall', '2023');
INSERT INTO `student_info` (`user_id`, `program`, `advisor_id`, `grad_semester`, `grad_year`) VALUES (88888888, 'masters', 4, 'fall', '2023');
INSERT INTO `student_info` (`user_id`, `program`, `advisor_id`, `grad_semester`, `grad_year`) VALUES (99999999, 'masters', 4, 'fall', '2023');

-- -----------------------------------------------------
-- Table `alumni_info`
-- -----------------------------------------------------
INSERT INTO `alumni_info` (`user_id`, `program`, `grad_year`) VALUES (77777777, 'masters', '2014');

-- -----------------------------------------------------
-- Table `faculty_info`
-- -----------------------------------------------------
INSERT INTO `faculty_info` (`user_id`, `department`, `is_advisor`, `is_reviewer`, `is_instructor`, `is_admissions_chair`) VALUES (3, 'CSCI', 1, 1, 1, 0); -- Narahari
INSERT INTO `faculty_info` (`user_id`, `department`, `is_advisor`, `is_reviewer`, `is_instructor`, `is_admissions_chair`) VALUES (4, 'CSCI', 1, 0, 1, 0); -- Parmer
INSERT INTO `faculty_info` (`user_id`, `department`, `is_advisor`, `is_reviewer`, `is_instructor`, `is_admissions_chair`) VALUES (7, 'CSCI', 0, 0, 1, 1); -- Choi
INSERT INTO `faculty_info` (`user_id`, `department`, `is_advisor`, `is_reviewer`, `is_instructor`, `is_admissions_chair`) VALUES (8, 'CSCI', 0, 1, 1, 0); -- Wood
INSERT INTO `faculty_info` (`user_id`, `department`, `is_advisor`, `is_reviewer`, `is_instructor`, `is_admissions_chair`) VALUES (9, 'CSCI', 0, 1, 1, 0); -- Heller

-- -----------------------------------------------------
-- Table `course`
-- -----------------------------------------------------
# 1
INSERT INTO `course` (`department`,`course_num`,`title`,`credits`, `required_masters`) VALUES ('CSCI', 6221,'SW Paradigms', 3, 1);
# 2
INSERT INTO `course` (`department`,`course_num`,`title`,`credits`, `required_masters`) VALUES ('CSCI', 6461, 'Computer Architecture', 3, 1);
# 3
INSERT INTO `course` (`department`,`course_num`,`title`,`credits`, `required_masters`) VALUES ('CSCI', 6212, 'Algorithms', 3, 1);
# 4
INSERT INTO `course` (`department`,`course_num`,`title`,`credits`) VALUES ('CSCI', 6220, 'Machine Learning', 3);
# 5
INSERT INTO `course` (`department`,`course_num`,`title`,`credits`) VALUES ('CSCI', 6232, 'Networks 1', 3);
# 6
INSERT INTO `course` (`department`,`course_num`,`title`,`credits`) VALUES ('CSCI', 6233, 'Networks 2', 3);
# 7
INSERT INTO `course` (`department`,`course_num`,`title`,`credits`) VALUES ('CSCI', 6241, 'Database 1', 3);
# 8
INSERT INTO `course` (`department`,`course_num`,`title`,`credits`) VALUES ('CSCI', 6242, 'Database 2', 3);
# 9
INSERT INTO `course` (`department`,`course_num`,`title`,`credits`) VALUES ('CSCI', 6246, 'Compilers', 3);
# 10
INSERT INTO `course` (`department`,`course_num`,`title`,`credits`) VALUES ('CSCI', 6260, 'Multimedia', 3);
# 11
INSERT INTO `course` (`department`,`course_num`,`title`,`credits`) VALUES ('CSCI', 6251, 'Cloud Computing', 3);
# 12
INSERT INTO `course` (`department`,`course_num`,`title`,`credits`) VALUES ('CSCI', 6254, 'SW Engineering', 3);
# 13
INSERT INTO `course` (`department`,`course_num`,`title`,`credits`) VALUES ('CSCI', 6262, 'Graphics 1', 3);
# 14
INSERT INTO `course` (`department`,`course_num`,`title`,`credits`) VALUES ('CSCI', 6283, 'Security 1', 3);
# 15
INSERT INTO `course` (`department`,`course_num`,`title`,`credits`) VALUES ('CSCI', 6284, 'Cryptography', 3);
# 16
INSERT INTO `course` (`department`,`course_num`,`title`,`credits`) VALUES ('CSCI', 6286, 'Network Security', 3);
#17
INSERT INTO `course` (`department`,`course_num`,`title`,`credits`) VALUES ('CSCI', 6325, 'Algorithms 2', 3);
# 18
INSERT INTO `course` (`department`,`course_num`,`title`,`credits`) VALUES ('CSCI', 6339, 'Embedded Systems', 3);
# 19
INSERT INTO `course` (`department`,`course_num`,`title`,`credits`) VALUES ('CSCI', 6384, 'Cryptography 2', 3);
# 20
INSERT INTO `course` (`department`,`course_num`,`title`,`credits`) VALUES ('ECE', 6241, 'Communication Theory', 3);
# 21
INSERT INTO `course` (`department`,`course_num`,`title`,`credits`) VALUES ('ECE', 6242, 'Information Theory', 2);
# 22
INSERT INTO `course` (`department`,`course_num`,`title`,`credits`) VALUES ('MATH', 6210, 'Logic', 2);

-- -----------------------------------------------------
-- Table `course_prereq`
-- -----------------------------------------------------
INSERT INTO `course_prereq` (`course_id`, `prereq_id`) VALUES (6, 5);
INSERT INTO `course_prereq` (`course_id`, `prereq_id`) VALUES (8, 7);
INSERT INTO `course_prereq` (`course_id`, `prereq_id`) VALUES (9, 2);
INSERT INTO `course_prereq` (`course_id`, `prereq_id`) VALUES (9, 3);
INSERT INTO `course_prereq` (`course_id`, `prereq_id`) VALUES (11, 2);
INSERT INTO `course_prereq` (`course_id`, `prereq_id`) VALUES (12, 1);
INSERT INTO `course_prereq` (`course_id`, `prereq_id`) VALUES (14, 3);
INSERT INTO `course_prereq` (`course_id`, `prereq_id`) VALUES (15, 3);
INSERT INTO `course_prereq` (`course_id`, `prereq_id`) VALUES (16, 14);
INSERT INTO `course_prereq` (`course_id`, `prereq_id`) VALUES (16, 5);
INSERT INTO `course_prereq` (`course_id`, `prereq_id`) VALUES (17, 3);
INSERT INTO `course_prereq` (`course_id`, `prereq_id`) VALUES (18, 2);
INSERT INTO `course_prereq` (`course_id`, `prereq_id`) VALUES (18, 3);
INSERT INTO `course_prereq` (`course_id`, `prereq_id`) VALUES (19, 15);

-- -----------------------------------------------------
-- Table `sections`
-- -----------------------------------------------------
# SW Paradigms
INSERT INTO `sections` (`course_id`, `csem`, `cyear`, `day_of_week`, `class_time`, `room`, `room_capacity`, `fid`) VALUES (1, 'fall', 2023, 'M', '15:00-17:30', 'Bell 101', 35, 3);
# Computer Architecture
INSERT INTO `sections` (`course_id`, `csem`, `cyear`, `day_of_week`, `class_time`, `room`, `room_capacity`, `fid`) VALUES (2, 'fall', 2023, 'T', '15:00-17:30', 'Bell 101', 35, 3);
# Algorithms
INSERT INTO `sections` (`course_id`, `csem`, `cyear`, `day_of_week`, `class_time`, `room`, `room_capacity`, `fid`) VALUES (3, 'fall', 2023, 'W', '15:00-17:30', 'Bell 101', 35, 7);
# Machine Learning
INSERT INTO `sections` (`course_id`, `csem`, `cyear`, `day_of_week`, `class_time`, `room`, `room_capacity`, `fid`) VALUES (4, 'fall', 2023, 'W', '15:00-17:30', 'Bell 101', 35, 7);
# Networks 1
INSERT INTO `sections` (`course_id`, `csem`, `cyear`, `day_of_week`, `class_time`, `room`, `room_capacity`, `fid`) VALUES (5, 'fall', 2023, 'M', '18:00-20:30', 'Bell 101', 35, 3);
# Networks 2
INSERT INTO `sections` (`course_id`, `csem`, `cyear`, `day_of_week`, `class_time`, `room`, `room_capacity`, `fid`) VALUES (6, 'fall', 2023, 'T', '18:00-20:30', 'Bell 101', 35, 3);
# Database 1
INSERT INTO `sections` (`course_id`, `csem`, `cyear`, `day_of_week`, `class_time`, `room`, `room_capacity`, `fid`) VALUES (7, 'fall', 2023, 'W', '18:00-20:30', 'Bell 101', 35, 3);
# Database 2
INSERT INTO `sections` (`course_id`, `csem`, `cyear`, `day_of_week`, `class_time`, `room`, `room_capacity`, `fid`) VALUES (8, 'fall', 2023, 'R', '18:00-20:30', 'Bell 101', 35, 3);
# Compilers
INSERT INTO `sections` (`course_id`, `csem`, `cyear`, `day_of_week`, `class_time`, `room`, `room_capacity`, `fid`) VALUES (9, 'fall', 2023, 'T', '15:00-17:30', 'Bell 101', 35, 3);
# Cloud Computing
INSERT INTO `sections` (`course_id`, `csem`, `cyear`, `day_of_week`, `class_time`, `room`, `room_capacity`, `fid`) VALUES (11, 'fall', 2023, 'M', '18:00-20:30', 'Bell 101', 35, 3);
# SW Engineering
INSERT INTO `sections` (`course_id`, `csem`, `cyear`, `day_of_week`, `class_time`, `room`, `room_capacity`, `fid`) VALUES (12, 'fall', 2023, 'M', '15:30-18:00', 'Bell 101', 35, 3);
# Multimedia
INSERT INTO `sections` (`course_id`, `csem`, `cyear`, `day_of_week`, `class_time`, `room`, `room_capacity`, `fid`) VALUES (10, 'fall', 2023, 'R', '18:00-20:30', 'Bell 101', 35, 3);
# Graphics 1
INSERT INTO `sections` (`course_id`, `csem`, `cyear`, `day_of_week`, `class_time`, `room`, `room_capacity`, `fid`) VALUES (13, 'fall', 2023, 'W', '18:00-20:30', 'Bell 101', 35, 3);
# Security 1
INSERT INTO `sections` (`course_id`, `csem`, `cyear`, `day_of_week`, `class_time`, `room`, `room_capacity`, `fid`) VALUES (14, 'fall', 2023, 'T', '18:00-20:30', 'Bell 101', 35, 3);
# Cryptography
INSERT INTO `sections` (`course_id`, `csem`, `cyear`, `day_of_week`, `class_time`, `room`, `room_capacity`, `fid`) VALUES (15, 'fall', 2023, 'M', '18:00-20:30', 'Bell 101', 35, 3);
# Network Security
INSERT INTO `sections` (`course_id`, `csem`, `cyear`, `day_of_week`, `class_time`, `room`, `room_capacity`, `fid`) VALUES (16, 'fall', 2023, 'W', '18:00-20:30', 'Bell 101', 35, 3);
# Algorithms 2
INSERT INTO `sections` (`course_id`, `csem`, `cyear`, `day_of_week`, `class_time`, `room`, `room_capacity`, `fid`) VALUES (17, 'fall', 2023, 'W', '18:00-20:30', 'Bell 101', 35, 3);
# Embedded Systems
INSERT INTO `sections` (`course_id`, `csem`, `cyear`, `day_of_week`, `class_time`, `room`, `room_capacity`, `fid`) VALUES (18, 'fall', 2023, 'R', '16:00-18:30', 'Bell 101', 35, 3);
# Cryptography 2
INSERT INTO `sections` (`course_id`, `csem`, `cyear`, `day_of_week`, `class_time`, `room`, `room_capacity`, `fid`) VALUES (19, 'fall', 2023, 'W', '15:00-17:30', 'Bell 101', 35, 3);
# Communication Theory
INSERT INTO `sections` (`course_id`, `csem`, `cyear`, `day_of_week`, `class_time`, `room`, `room_capacity`, `fid`) VALUES (20, 'fall', 2023, 'M', '18:00-20:30', 'Bell 101', 35, 3);
# Information Theory
INSERT INTO `sections` (`course_id`, `csem`, `cyear`, `day_of_week`, `class_time`, `room`, `room_capacity`, `fid`) VALUES (21, 'fall', 2023, 'T', '18:00-20:30', 'Bell 101', 35, 3);
# Logic
INSERT INTO `sections` (`course_id`, `csem`, `cyear`, `day_of_week`, `class_time`, `room`, `room_capacity`, `fid`) VALUES (22, 'fall', 2023, 'W', '18:00-20:30', 'Bell 101', 35, 3);

-- -----------------------------------------------------
-- Table `student_courses`
-- -----------------------------------------------------
INSERT INTO `student_courses` (`user_id`, `course_id`, `semester`, `year`, `grade`) VALUES (88888888, '2', 'fall', '2023', 'IP'); -- Billie Holiday CSCI 6461
INSERT INTO `student_courses` (`user_id`, `course_id`, `semester`, `year`, `grade`) VALUES (88888888, '3', 'fall', '2023', 'IP'); -- Billie Holiday CSCI 6212
INSERT INTO `student_courses` (`user_id`, `course_id`, `semester`, `year`, `grade`) VALUES (55555555, '1', 'fall', '2023', 'A');
INSERT INTO `student_courses` (`user_id`, `course_id`, `semester`, `year`, `grade`) VALUES (55555555, '3', 'fall', '2023', 'A');
INSERT INTO `student_courses` (`user_id`, `course_id`, `semester`, `year`, `grade`) VALUES (55555555, '2', 'fall', '2023', 'A');
INSERT INTO `student_courses` (`user_id`, `course_id`, `semester`, `year`, `grade`) VALUES (55555555, '5', 'fall', '2023', 'A');
INSERT INTO `student_courses` (`user_id`, `course_id`, `semester`, `year`, `grade`) VALUES (55555555, '6', 'fall', '2023', 'A');
INSERT INTO `student_courses` (`user_id`, `course_id`, `semester`, `year`, `grade`) VALUES (55555555, '7', 'fall', '2023', 'B');
INSERT INTO `student_courses` (`user_id`, `course_id`, `semester`, `year`, `grade`) VALUES (55555555, '9', 'fall', '2023', 'B');
INSERT INTO `student_courses` (`user_id`, `course_id`, `semester`, `year`, `grade`) VALUES (55555555, '13', 'fall', '2023', 'B');
INSERT INTO `student_courses` (`user_id`, `course_id`, `semester`, `year`, `grade`) VALUES (55555555, '14', 'fall', '2023', 'B');
INSERT INTO `student_courses` (`user_id`, `course_id`, `semester`, `year`, `grade`) VALUES (55555555, '8', 'fall', '2023', 'B');

INSERT INTO `student_courses` (`user_id`, `course_id`, `semester`, `year`, `grade`) VALUES (66666666, '21', 'fall', '2023', 'C');
INSERT INTO `student_courses` (`user_id`, `course_id`, `semester`, `year`, `grade`) VALUES (66666666, '1', 'fall', '2023', 'B');
INSERT INTO `student_courses` (`user_id`, `course_id`, `semester`, `year`, `grade`) VALUES (66666666, '2', 'fall', '2023', 'B');
INSERT INTO `student_courses` (`user_id`, `course_id`, `semester`, `year`, `grade`) VALUES (66666666, '3', 'fall', '2023', 'B');
INSERT INTO `student_courses` (`user_id`, `course_id`, `semester`, `year`, `grade`) VALUES (66666666, '5', 'fall', '2023', 'B');
INSERT INTO `student_courses` (`user_id`, `course_id`, `semester`, `year`, `grade`) VALUES (66666666, '6', 'fall', '2023', 'B');
INSERT INTO `student_courses` (`user_id`, `course_id`, `semester`, `year`, `grade`) VALUES (66666666, '7', 'fall', '2023', 'B');
INSERT INTO `student_courses` (`user_id`, `course_id`, `semester`, `year`, `grade`) VALUES (66666666, '8', 'fall', '2023', 'B');
INSERT INTO `student_courses` (`user_id`, `course_id`, `semester`, `year`, `grade`) VALUES (66666666, '14', 'fall', '2023', 'B');
INSERT INTO `student_courses` (`user_id`, `course_id`, `semester`, `year`, `grade`) VALUES (66666666, '15', 'fall', '2023', 'B');

INSERT INTO `student_courses` (`user_id`, `course_id`, `semester`, `year`, `grade`) VALUES (1, '1', 'fall', '2023', 'A');
INSERT INTO `student_courses` (`user_id`, `course_id`, `semester`, `year`, `grade`) VALUES (1, '2', 'fall', '2023', 'A');
INSERT INTO `student_courses` (`user_id`, `course_id`, `semester`, `year`, `grade`) VALUES (1, '3', 'fall', '2023', 'A');
INSERT INTO `student_courses` (`user_id`, `course_id`, `semester`, `year`, `grade`) VALUES (1, '4', 'fall', '2023', 'A');
INSERT INTO `student_courses` (`user_id`, `course_id`, `semester`, `year`, `grade`) VALUES (1, '5', 'fall', '2023', 'A');
INSERT INTO `student_courses` (`user_id`, `course_id`, `semester`, `year`, `grade`) VALUES (1, '6', 'fall', '2023', 'A');
INSERT INTO `student_courses` (`user_id`, `course_id`, `semester`, `year`, `grade`) VALUES (1, '7', 'fall', '2023', 'A');
INSERT INTO `student_courses` (`user_id`, `course_id`, `semester`, `year`, `grade`) VALUES (1, '8', 'fall', '2023', 'A');
INSERT INTO `student_courses` (`user_id`, `course_id`, `semester`, `year`, `grade`) VALUES (1, '9', 'fall', '2023', 'A');
INSERT INTO `student_courses` (`user_id`, `course_id`, `semester`, `year`, `grade`) VALUES (1, '10', 'fall', '2023', 'A');
INSERT INTO `student_courses` (`user_id`, `course_id`, `semester`, `year`, `grade`) VALUES (1, '11', 'fall', '2023', 'A');
INSERT INTO `student_courses` (`user_id`, `course_id`, `semester`, `year`, `grade`) VALUES (1, '12', 'fall', '2023', 'A');

INSERT INTO `student_courses` (`user_id`, `course_id`, `semester`, `year`, `grade`) VALUES (77777777, '1', 'fall', '2023', 'B');
INSERT INTO `student_courses` (`user_id`, `course_id`, `semester`, `year`, `grade`) VALUES (77777777, '3', 'fall', '2023', 'B');
INSERT INTO `student_courses` (`user_id`, `course_id`, `semester`, `year`, `grade`) VALUES (77777777, '2', 'fall', '2023', 'B');
INSERT INTO `student_courses` (`user_id`, `course_id`, `semester`, `year`, `grade`) VALUES (77777777, '5', 'fall', '2023', 'B');
INSERT INTO `student_courses` (`user_id`, `course_id`, `semester`, `year`, `grade`) VALUES (77777777, '6', 'fall', '2023', 'B');
INSERT INTO `student_courses` (`user_id`, `course_id`, `semester`, `year`, `grade`) VALUES (77777777, '7', 'fall', '2023', 'B');
INSERT INTO `student_courses` (`user_id`, `course_id`, `semester`, `year`, `grade`) VALUES (77777777, '8', 'fall', '2023', 'B');
INSERT INTO `student_courses` (`user_id`, `course_id`, `semester`, `year`, `grade`) VALUES (77777777, '14', 'fall', '2023', 'A');
INSERT INTO `student_courses` (`user_id`, `course_id`, `semester`, `year`, `grade`) VALUES (77777777, '15', 'fall', '2023', 'A');
INSERT INTO `student_courses` (`user_id`, `course_id`, `semester`, `year`, `grade`) VALUES (77777777, '16', 'fall', '2023', 'A');

-- --------------------------------------------------------
-- Table `degree_requirements`
-- --------------------------------------------------------
INSERT INTO `degree_requirements` VALUES ('masters', 'min_gpa', 3.0);
INSERT INTO `degree_requirements` VALUES ('masters', 'min_credit_hours', 30);
INSERT INTO `degree_requirements` VALUES ('masters', 'most_non_cs_courses', 2);
INSERT INTO `degree_requirements` VALUES ('masters', 'most_below_b_grades', 2);
INSERT INTO `degree_requirements` VALUES ('phd', 'min_gpa', 3.5);
INSERT INTO `degree_requirements` VALUES ('phd', 'min_credit_hours', 36);
INSERT INTO `degree_requirements` VALUES ('phd', 'min_cs_credit_hours', 30);
INSERT INTO `degree_requirements` VALUES ('phd', 'most_below_b_grades', 1);
INSERT INTO `degree_requirements` VALUES ('phd', 'thesis_passed', 1);

-- --------------------------------------------------------
-- Table `alumni_chat_messgages`
-- --------------------------------------------------------
INSERT INTO `alumni_chat_messages` (`user_id`, `message`) VALUES (66666666, 'Hello World');
INSERT INTO `alumni_chat_messages` (`user_id`, `message`) VALUES (5, 'How\'s it going?');