from flask import Blueprint, flash, session, render_template, redirect, url_for, request
from datetime import datetime, date
from helpers import login_required, authorize, myDb
from transcript import gradeConversion

import random, re

regs = Blueprint('regs', __name__, template_folder='templates/regs')

def _process_time(class_time):
    time_list = class_time.split("-")

    start_time = float(time_list[0][0:2])
    if str(time_list[0][3]) != '0':
        start_time += 0.5

    end_time = float(time_list[1][0:2])
    if str(time_list[1][3]) != '0':
        end_time += 0.5

    return start_time, end_time

def _get_curr_semester():
    seasons = {
            'Spring': ['August','September', 'October', 'November', 'December'],
            'Fall': ['January', 'February', 'March', 'April', 'May', 'June']
            }
    
    current_time = datetime.now()
    current_month = current_time.strftime('%B')
    current_year = int(current_time.strftime('%Y'))

    for season in seasons:
        if current_month in seasons[season]:
            if season == 'Spring':
                current_year += 1
            return season, current_year
    return 'Invalid input month'

# Remove from registration 
@regs.route('/<id>/remove', methods=['GET', 'POST'])
def remove(id):
    cursor = myDb.cursor(dictionary=True)

    # ensure advising form is approved
    cursor.execute("SELECT `advising_form_approved` FROM `student_info` WHERE `user_id` = %s", (id,))
    approved = cursor.fetchone()['advising_form_approved']
    if not approved:
        flash("You cannot register until your advising form has been approved and the hold has been lifted.", "danger")
        myDb.commit()
        cursor.close()
        return redirect(url_for("ads.students.advising_form"))
    
    if request.method == 'POST':
        session["registration"].remove(request.form["course_id"])
        session.modified = True

    myDb.commit()
    cursor.close()
    return redirect(url_for("regs.register", id=id))


# Route to add a class
@regs.route('/<id>/add', methods=['GET', 'POST'])
@login_required
@authorize(['student'])
def add(id):
    cursor = myDb.cursor(dictionary=True)

    # ensure advising form is approved
    cursor.execute("SELECT `advising_form_approved` FROM `student_info` WHERE `user_id` = %s", (id,))
    approved = cursor.fetchone()['advising_form_approved']
    if not approved:
        flash("You cannot register until your advising form has been approved and the hold has been lifted.", "danger")
        myDb.commit()
        cursor.close()
        return redirect(url_for("ads.students.advising_form"))
    
    if request.method == 'POST':
        # Retrieve form data
        cid = request.form["course_id"]

         # 1. Check if class already in currently registered class
        if cid in session["registration"]:
            flash("You've already registered for that class", "danger")
            myDb.commit()
            cursor.close()
            return redirect(url_for("regs.register", id=id))


        # Check if already enrolled previously
        cursor.execute("SELECT * FROM student_courses WHERE course_id = %s AND user_id = %s", (cid, id))
        data = cursor.fetchone()
        if data:
            flash("You've already taken that class", "danger")
            myDb.commit()
            cursor.close()
            return redirect(url_for("regs.register", id=id)) 

        # Check prereq
        cursor.execute("SELECT * FROM course_prereq WHERE course_id = %s", (cid,))
        prereq_list = cursor.fetchall()
        for prereq in prereq_list:
            cursor.execute('''SELECT * FROM student_courses WHERE user_id = %s AND course_id = %s''', (id, prereq['prereq_id']))
            prereq = cursor.fetchall()
            
            if not prereq:
                flash("You do not fulfill the prerequisites for this class", "danger")
                myDb.commit()
                cursor.close()
                return redirect(url_for("regs.register", id=id))

        # Check schedule conflict
        my_time = request.form["class_time"]
        my_class_time = _process_time(my_time)
        
         # Retrieve all class times for currently registering year and semester for each class and check
        for class_id in session["registration"]:
            cursor.execute("SELECT day_of_week, class_time FROM sections WHERE course_id = %s AND csem = %s \
                           AND cyear = %s", (class_id, request.form["csem"], request.form["cyear"]))
            
            other_class = cursor.fetchone()
            if other_class['day_of_week'] != request.form['day_of_week']:
                continue
            other_time = other_class['class_time']
            curr_class_time =  _process_time(other_time)

            if (my_class_time[0] > curr_class_time[0] - 0.5 and my_class_time[0] < curr_class_time[1] + 0.5) or (my_class_time[1] > curr_class_time[0] - 0.5 and my_class_time[1] < curr_class_time[1] + 0.5):
                flash("Schedule conflict, oops", "danger")
                myDb.commit()
                cursor.close()
                return redirect(url_for("regs.register", id=id)) 
          

        # Now we have to check for the classes that already got checked out but for current semester/year
        cursor.execute("SELECT day_of_week, class_time FROM sections s JOIN student_courses sc ON s.course_id = sc.course_id AND s.csem = sc.semester AND s.cyear = sc.year \
                       WHERE s.csem = %s AND s.cyear = %s AND user_id = %s", (request.form["csem"], request.form["cyear"], id))
        time_list = cursor.fetchall()
        for curr_class in time_list:
            if curr_class['day_of_week'] != request.form['day_of_week']:
                continue
            curr_class_time = _process_time(curr_class['class_time'])
            if (my_class_time[0] > curr_class_time[0] - 0.5 and my_class_time[0] < curr_class_time[1] + 0.5) or (my_class_time[1] > curr_class_time[0] - 0.5 and my_class_time[1] < curr_class_time[1] + 0.5):
                flash("Schedule conflict, oops", "danger")
                myDb.commit()
                cursor.close()
                return redirect(url_for("regs.register", id=id)) 
            
        # check if class is full
        cursor.execute("SELECT COUNT(user_id) AS enrollment FROM student_courses WHERE course_id = %s AND semester = %s AND year = %s", (cid, request.form["csem"], request.form["cyear"]))
        enrollment = cursor.fetchone()['enrollment']
        cursor.execute("SELECT room_capacity FROM sections WHERE course_id = %s AND csem = %s AND cyear = %s", (cid, request.form["csem"], request.form["cyear"]))
        capacity = cursor.fetchone()['room_capacity']
        print(enrollment, capacity)
        if enrollment >= capacity:
            flash("Class is full", "danger")
            myDb.commit()
            cursor.close()
            return redirect(url_for("regs.register", id=id))


        # If no issue, then add to registered class
        session["registration"].append(cid)
        session.modified = True

    myDb.commit()
    cursor.close()
    return redirect(url_for("regs.register", id=id))


@regs.route('/<id>/checkout', methods=['GET', 'POST'])
@login_required
@authorize(['student'])
def checkout(id):
    cursor = myDb.cursor(dictionary=True)

    # ensure advising form is approved
    cursor.execute("SELECT `advising_form_approved` FROM `student_info` WHERE `user_id` = %s", (id,))
    approved = cursor.fetchone()['advising_form_approved']
    if not approved:
        flash("You cannot register until your advising form has been approved and the hold has been lifted.", "danger")
        myDb.commit()
        cursor.close()
        return redirect(url_for("ads.students.advising_form"))
    
    # Commit data to enrollment table
    if request.method == 'POST':
        semester = _get_curr_semester()
        for cid in session["registration"]:
            cursor.execute("INSERT INTO student_courses (user_id, course_id, semester, year) VALUES (%s, %s, %s, %s)", (id, cid, semester[0], semester[1]))
            myDb.commit()

        session["registration"] = []
        session.modified = True

        flash("You've successfully registered", "success")

    myDb.commit()
    cursor.close()
    return redirect(url_for("regs.register", id=id)) 


# Class registration page
@regs.route('/register', methods=['GET', 'POST'])
@login_required
@authorize(['student'])
def register():
    id = session['id']
    
    # Connect to database
    cursor = myDb.cursor(dictionary=True)

    # ensure advising form is approved
    cursor.execute("SELECT `advising_form_approved` FROM `student_info` WHERE `user_id` = %s", (id,))
    approved = cursor.fetchone()['advising_form_approved']
    if not approved:
        flash("You cannot register until your advising form has been approved and the hold has been lifted.", "danger")
        myDb.commit()
        cursor.close()
        return redirect(url_for("ads.students.advising_form"))

    semester = _get_curr_semester()
    query = "SELECT * FROM sections sec JOIN course c ON sec.course_id = c.id \
            WHERE sec.csem = %s AND sec.cyear = %s"
    params = [semester[0], semester[1]]

    # Display the courses
    dname = request.args.get("department")
    cnum = request.args.get("course_num")
    title = request.args.get("course_title")

    if dname != None and dname != "":
        query += " AND c.department LIKE  %s"
        params.append(f"%{dname}%")
    
    if cnum != None and cnum != "":
        query += " AND c.course_num = %s"
        params.append(cnum)

    if title != None and title != "":
        query += " AND c.title LIKE %s"
        params.append(f"%{title}%")
   
    cursor.execute(query, params)
    classes = cursor.fetchall()

    instructor_list = {}
    for each_class in classes:
        cursor.execute("SELECT first_name, last_name FROM user WHERE id = %s", (each_class['fid'],))
        instructor_list[each_class['fid']] = cursor.fetchone()

        # get prereqs
        cursor.execute("SELECT * FROM course_prereq p JOIN course c ON p.prereq_id = c.id WHERE p.course_id = %s", (each_class['course_id'],))
        prereq = cursor.fetchall()
        each_class['prereq'] = prereq

    # Get the classes that the student is currently registered for
    registered = []
    for cid in session["registration"]:
        cursor.execute("SELECT * FROM sections JOIN course on sections.course_id = course.id WHERE course_id = %s AND csem = %s AND cyear = %s", (cid, semester[0], semester[1]))
        course = cursor.fetchone()

        # Get the instructor
        cursor.execute("SELECT first_name, last_name FROM user WHERE id = %s", (course['fid'],))
        course['instructor'] = cursor.fetchone()

        # Get the prereqs
        cursor.execute("SELECT * FROM course_prereq p JOIN course c ON p.prereq_id = c.id WHERE p.course_id = %s", (course['course_id'],))
        prereq = cursor.fetchall()
        course['prereq'] = prereq

        registered.append(course)
    

    renderer = {
        "course_id": "Class ID",
        "csem": "Semester",
        "cyear": "Year",
        "day_of_week": "Day of Week",
        "class_time": "Class Time",
        "fid": "Instructor",
        "department": "Department",
        "course_num": "Course Number",
        "class_section": "Class Section",
        "title": "Title",
        "credits": "Credits",
        "room": "Location",
        "room_capacity": "Capacity",
    }

    cursor.execute("SELECT * FROM student_courses sc JOIN sections s ON sc.course_id = s.course_id AND sc.semester = s.csem AND sc.year = s.cyear \
                   JOIN course c ON s.course_id = c.id WHERE \
                   sc.user_id = %s AND sc.semester = %s AND sc.year = %s", (session['id'], semester[0], semester[1]))
    schedule = cursor.fetchall()

    # get department list
    cursor.execute("SELECT DISTINCT department FROM course ORDER BY department ASC")
    dept = cursor.fetchall()
    myDb.commit()
    cursor.close()

    return render_template('registration.html', schedule=schedule, renderer=renderer, instructor_list=instructor_list, classes=classes, session=session, semester=semester, departments=dept, registered=registered)

# Remove course from schedule
@regs.route('/remove_course', methods=['GET', 'POST'])
@login_required
@authorize(['registrar'])
def remove_course():
    if request.method == 'POST':
        course_id = request.form.get('course_id')
        csem = request.form.get('csem')
        cyear = request.form.get('cyear')

        # Connect to database
        cursor = myDb.cursor(dictionary=True)
        # Delete course and corresponding sections from schedule of classes
        cursor.execute("DELETE FROM sections s WHERE s.course_id = %s AND s.csem = %s AND s.cyear = %s", (course_id, csem, cyear,))
        # Delete course from student schedule
        cursor.execute("DELETE FROM student_courses sc WHERE sc.course_id = %s AND sc.semester = %s AND sc.year = %s", (course_id, csem, cyear,))
        # Delete course from course table
        cursor.execute("DELETE FROM course c WHERE c.id = %s", (course_id,))
        # Commit changes
        myDb.commit()
        cursor.close()
        # Return to schedule page
        return redirect(url_for('regs.schedule'))

# Add course to schedule
@regs.route('/add_course', methods=['GET', 'POST'])
@login_required
@authorize(['registrar'])
def add_course():
    # Connect to database
    cursor = myDb.cursor(dictionary=True)
    # Get course information from form
    department = request.form.get('department')
    course_num = int(request.form.get('course_num'))
    title = request.form.get('course')
    credits = int(request.form.get('credits'))
    req_masters = int(request.form.get('req_masters'))
    # Get section information from form
    day_of_week = request.form.get('day_of_week')
    time = request.form.get('time')
    room = request.form.get('room')
    room_capacity = request.form.get('room_capacity')
    # Get instructor information from form
    fid = request.form.get('fid')

    # Verify if course department, number, and title are valid
    if department in ['', None] or course_num in ['', None] or title in ['', None]:
        myDb.commit()
        cursor.close()
        return redirect(url_for('regs.schedule'))
    if department in ['CSCI', 'ECE', 'MATH']:
        pass
    
    # Verify if instructor ID is valid
    cursor.execute("SELECT * FROM faculty_info f WHERE f.user_id = %s", (fid,))
    instructor = cursor.fetchone()
    if instructor == None:
        myDb.commit()
        cursor.close()
        return redirect(url_for('regs.schedule'))
    
    # Check if course already exists
    cursor.execute("SELECT * FROM course c WHERE c.department = %s AND c.course_num = %s", (department, course_num,))
    course = cursor.fetchone()
    if course == None:
        # Insert into courses table
        cursor.execute("INSERT INTO course (department, course_num, title, credits, required_masters) VALUES (%s, %s, %s, %s, %s)", (department, course_num, title, credits, req_masters,))
        myDb.commit()

    # verify if insertion into courses table worked
    cursor.execute("SELECT * FROM course WHERE department = %s AND course_num = %s", (department, course_num,))
    course = cursor.fetchone()

    # Get course id
    # cursorA = cursor.cursor(buffered=True)
    cursor.execute("SELECT id FROM course WHERE department = %s AND course_num = %s", (department, course_num,))
    course_id = cursor.fetchone()['id']
    # Get current semester and year
    semester_and_year = _get_curr_semester()
    csem = semester_and_year[0]
    cyear = semester_and_year[1]
    
    # Check if section already exists
    cursor.execute("SELECT * FROM sections s WHERE s.course_id = %s AND s.csem = %s AND s.cyear = %s", (course_id, csem, cyear,))
    section = cursor.fetchone()
    if section == None:
        # Insert into sections table
        cursor.execute("INSERT INTO sections (course_id, csem, cyear, day_of_week, class_time, room, room_capacity, fid) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)", (course_id, csem, cyear, day_of_week, time, room, room_capacity, fid,))
        myDb.commit()

    # Verify if insertion into sections table worked 
    cursor.execute("SELECT * FROM sections s WHERE s.course_id = %s AND s.csem = %s AND s.cyear = %s", (course_id, csem, cyear,))
    section = cursor.fetchone()
    myDb.commit()
    cursor.close()

    return redirect(url_for('regs.schedule'))

# Edit schedule of classes page
@regs.route('/schedule', methods=['GET', 'POST'])
@login_required
@authorize(['registrar'])
def schedule():
    # Connect to database
    cursor = myDb.cursor(dictionary=True)
    # Get current semester and year
    semester = _get_curr_semester()

    # Get classes for all semesters
    query = "SELECT * FROM sections s JOIN course c ON s.course_id = c.id JOIN user u ON s.fid = u.id \
            WHERE s.csem = %s AND s.cyear = %s"
    params = [semester[0], semester[1]]

    dname = request.args.get("dname")
    cnum = request.args.get("cnum")
    ctitle = request.args.get("ctitle")
            
    if dname != None and dname != "":
        query += " AND c.department LIKE %s"
        params.append(f"%{dname}%")
    
    if cnum != None and cnum != "":
        query += " AND c.course_num = %s"
        params.append(cnum)

    if ctitle != None and ctitle != "":
        query += " AND c.title LIKE %s"
        params.append(f"%{ctitle}%")
   
    cursor.execute(query, params)
    classes = cursor.fetchall()

    cursor.execute("SELECT csem, cyear FROM sections s GROUP BY s.csem, s.cyear ORDER BY s.cyear DESC, s.csem")
    semesters = cursor.fetchall()   

    # get department list
    cursor.execute("SELECT DISTINCT department FROM course ORDER BY department ASC")
    dept = cursor.fetchall()
    myDb.commit()
    cursor.close()

    return render_template('schedule.html', dept=dept, semesters=semesters, classes=classes, curr_semester=semester[0], curr_year=semester[1])

# Course catalog page
@regs.route('/catalog')
@login_required
@authorize(['student','sysadmin','gs','faculty', 'registrar'])
def catalog():
    cursor = myDb.cursor(dictionary=True)
    cursor.execute("SELECT department FROM course GROUP BY department ORDER BY department ASC")
    dept = cursor.fetchall()
    course = {}
    for row in dept:
        cursor.execute("SELECT * FROM course WHERE department = %s", (row["department"],))
        course[row["department"]] = cursor.fetchall()
        # get prereqs
        for c in course[row["department"]]:
            cursor.execute("SELECT course_prereq.*, course.department, course.course_num FROM course_prereq INNER JOIN course ON course.id = course_prereq.prereq_id WHERE course_id = %s", (c["id"],))
            c["prereq"] = cursor.fetchall()

    myDb.commit()
    cursor.close()
    return render_template('catalog.html', dept=dept, course=course)


# Drop courses
@regs.route('/drop', methods=['GET', 'POST'])
@login_required
@authorize(['student'])
def drop():
    cursor = myDb.cursor(dictionary=True)

    # ensure advising form is approved
    cursor.execute("SELECT `advising_form_approved` FROM `student_info` WHERE `user_id` = %s", (session['userId'],))
    approved = cursor.fetchone()['advising_form_approved']
    if not approved:
        flash("You cannot register until your advising form has been approved and the hold has been lifted.", "danger")
        myDb.commit()
        cursor.close()
        return redirect(url_for("ads.students.advising_form"))
    
    if request.method == 'POST':
        stud_id = request.form['stud_id']
        cid = request.form["cid"]
        csem = request.form["csem"]
        cyear = request.form["cyear"]

        cursor.execute("DELETE FROM student_courses WHERE user_id = %s AND course_id = %s AND semester = %s AND year = %s", (stud_id, cid, csem, cyear))
        myDb.commit()

    myDb.commit()
    cursor.close()
    return redirect(url_for('regs.register', id=session['id']))

@regs.route("/update_grade", methods=['GET', 'POST'])
@login_required
@authorize(['faculty', 'sysadmin', 'gs', 'registrar'])
def update_grade():
    cursor = myDb.cursor(dictionary=True)

    if request.method == 'POST':
        cursor = myDb.cursor(dictionary=True)

        grade = request.form['grade']
        student_id = request.form['student_id'] 
        class_id = request.form['class_id']

        # get current grade
        cursor.execute("SELECT grade FROM student_courses WHERE user_id = %s AND course_id = %s", (student_id, class_id))
        current_grade = cursor.fetchone()

        if current_grade['grade'] != "IP" and session['userType'] == "faculty":
            flash("You cannot update a grade that has already been posted", "danger")
            myDb.commit()
            cursor.close()
            return redirect(url_for('regs.update_grade'))

        cursor.execute("UPDATE student_courses SET grade = %s WHERE user_id = %s AND course_id = %s", (grade, student_id, class_id))
        myDb.commit()

        flash("Grade updated successfully", "success")

    # Get list of sections/courses
    query = "SELECT * FROM sections s JOIN course c ON s.course_id = c.id"
    params = []
    if session['userType'] == "faculty":
        query += " WHERE s.fid = %s"
        params.append(session['userId'])

    cursor.execute(query, params)
    sections = cursor.fetchall()

    # Get list of students
    students = []
    semester = _get_curr_semester()
    if request.args.get('class'):
        cursor.execute("SELECT * FROM student_courses sc JOIN user u ON sc.user_id = u.id WHERE sc.course_id = %s AND sc.semester = %s AND sc.year = %s", (request.args.get('class'), semester[0], semester[1]))
        students = cursor.fetchall()
    
    myDb.commit()
    cursor.close()
    return render_template('grades.html', grades=gradeConversion, classes=sections, students=students)


