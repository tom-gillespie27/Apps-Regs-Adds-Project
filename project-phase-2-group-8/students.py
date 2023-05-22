from flask import render_template, request, redirect, url_for, flash, Blueprint, session, abort
from helpers import authorize, myDb, login_required

students = Blueprint('students', __name__, template_folder='templates')

programTypes = {
    "masters": "Masters",
    "phd": "PhD"
}

@students.route("/")
@login_required
@authorize(["faculty", "gs", "sysadmin"])
def index():
    cursor = myDb.cursor(dictionary=True)
    advisors = None
    
    advisor = request.args.get('advisorId')
    year = request.args.get('year')
    degree = request.args.get('degree')

    params = []

    query = ""

    if session['userType'] == "faculty":
        # query for students
        query += "SELECT `user_id`, `program`, `grad_status`, `thesis_passed`, `form_approved`, `advising_form_approved`, `first_name`, `last_name` FROM `student_info` INNER JOIN `user` ON `student_info`.`user_id` = `user`.`id` WHERE `advisor_id` = %s"
        params.append(session["userId"])
    else:
        # Get the list of faculty advisors
        cursor.execute("SELECT `id`, `first_name`, `last_name` FROM `faculty_info` INNER JOIN `user` on `user`.`id` = `faculty_info`.`user_id` WHERE `is_advisor` = 1 ORDER BY `first_name`, `last_name`")
        advisors = cursor.fetchall()

        query += "SELECT `student_info`.`user_id`, `student_info`.`program`, `student_info`.`grad_status`, `student_info`.`grad_semester`, `student_info`.`grad_year`, `student_info`.`advisor_id`, `student_info`.`form_approved`, `student_info`.`advising_form_approved`, `student_info`.`thesis_passed`, `student`.`first_name`, `student`.`last_name`, `advisor`.`first_name` AS `advisor_first_name`, `advisor`.`last_name` AS `advisor_last_name` FROM `student_info` INNER JOIN `user` AS `student` ON `student_info`.`user_id` = `student`.`id` LEFT JOIN `user` AS `advisor` ON `student_info`.`advisor_id` = `advisor`.`id`"
    
        query += " WHERE 1=1" # fix for if filters show up...

    if advisor != None and advisor != "":
        query += " AND `student_info`.`advisor_id` = %s"
        params.append(advisor)
    if year != None and year != "":
        query += " AND `student_info`.`admit_year` = %s"
        params.append(year)
    if degree != None and degree != "":
        query += " AND `student_info`.`program` = %s"
        params.append(degree)

    cursor.execute(query, tuple(params))
    students = cursor.fetchall()

    # check if student has submitted form1
    for student in students:
        cursor.execute("SELECT COUNT(`course_id`) FROM `student_courses_planned` WHERE `user_id` = %s AND `form` = 'form1'", (student['user_id'],))
        student['form1_submitted'] = cursor.fetchone()['COUNT(`course_id`)'] > 0

    cursor.execute("SELECT DISTINCT `admit_year` AS `year` FROM `student_info` ORDER BY `year` DESC")
    years = cursor.fetchall()

    # check if student has submitted advising form
    for student in students:
        cursor.execute("SELECT COUNT(`course_id`) FROM `student_courses_planned` WHERE `user_id` = %s AND `form` = 'advising'", (student['user_id'],))
        student['advising_form_submitted'] = cursor.fetchone()['COUNT(`course_id`)'] > 0

    myDb.commit()
    cursor.close()

    return render_template("students_index.html",
                           students = students,
                           programTypes = programTypes, 
                           advisors = advisors, 
                           selectedAdvisor = int(request.args.get("advisorId")) if request.args.get("advisorId") else None,
                           years = years)

@students.route("/<int:studentId>/pass-thesis")
@login_required
@authorize(["faculty", "sysadmin"])
def passThesis(studentId):
    cursor = myDb.cursor(dictionary=True)

    # ensure advisor is assigned to student
    cursor.execute("SELECT `advisor_id` FROM `student_info` WHERE `user_id` = %s", (studentId,))
    advisorId = cursor.fetchone()['advisor_id']
    if session['userType'] == "advisor" and advisorId != session['userId']:
        flash("You are not assigned to this student.", "danger")
        myDb.commit()
        cursor.close()
        return redirect(url_for('.index'))

    # ensure student is PhD
    cursor.execute("SELECT `program` FROM `student_info` WHERE `user_id` = %s", (studentId,))
    program = cursor.fetchone()['program']
    if program != "phd":
        flash("Only PhD students can pass their thesis.", "danger")
        myDb.commit()
        cursor.close()
        return redirect(url_for('.index'))

    # update thesis status
    cursor.execute("UPDATE `student_info` SET `thesis_passed` = 1 WHERE `user_id` = %s", (studentId,))
    myDb.commit()

    cursor.close()
    return redirect(url_for('.index'))

@students.route("/<int:studentId>/form/review")
@login_required
@authorize(["faculty", "gs", "student", "sysadmin"])
def form_review(studentId):
    cursor = myDb.cursor(dictionary=True)

    if session["userType"] == "student" and session["userId"] != studentId:
        # student can only view their own form
        abort(401)

    # ensure advisor is assigned to student
    if session["userType"] == "faculty":
        cursor.execute("SELECT `advisor_id` FROM `student_info` WHERE `user_id` = %s", (studentId,))
        advisorId = cursor.fetchone()['advisor_id']
        if advisorId != session['userId']:
            flash("You are not assigned to this student.", "danger")
            myDb.commit()
            cursor.close()
            return redirect(url_for('.index'))


    # ensure student has courses on form1
    cursor.execute("SELECT COUNT(`course_id`) FROM `student_courses_planned` WHERE `user_id` = %s AND `form` = 'form1'", (studentId,))
    form1 = cursor.fetchone()['COUNT(`course_id`)']
    if form1 == 0 and session["userType"] != "student":
        flash("Student has not submitted a form1.", "danger")
        myDb.commit()
        cursor.close()
        return redirect(url_for('.index'))
    elif form1 == 0 and session["userType"] == "student":
        myDb.commit()
        cursor.close()
        return redirect(url_for('ads.view_form1'))

    # get courses on form1
    cursor.execute("SELECT `department`, `course_num`, `title` FROM `student_courses_planned` INNER JOIN `course` ON `course`.`id` = `student_courses_planned`.`course_id` WHERE `user_id` = %s AND `form` = 'form1'", (studentId,))
    courses = cursor.fetchall()

    # get student info
    cursor.execute("SELECT `id`, `first_name`, `last_name`, `program`, `form_approved` FROM `student_info` INNER JOIN `user` ON `student_info`.`user_id` = `user`.`id` WHERE `user_id` = %s", (studentId,))
    student = cursor.fetchone()

    myDb.commit()
    cursor.close()
    return render_template("students_review_form.html", courses=courses, student=student, programTypes=programTypes)

@students.route("/<int:studentId>/form/approve")
@login_required
@authorize(["faculty", "sysadmin"])
def form_approve(studentId):
    cursor = myDb.cursor(dictionary=True)

    # ensure advisor is assigned to student
    cursor.execute("SELECT `advisor_id` FROM `student_info` WHERE `user_id` = %s", (studentId,))
    advisorId = cursor.fetchone()['advisor_id']
    if session['userType'] == "advisor" and advisorId != session['userId']:
        flash("You are not assigned to this student.", "danger")
        myDb.commit()
        cursor.close()
        return redirect(url_for('.index'))

    # ensure student has courses on form1
    cursor.execute("SELECT COUNT(`course_id`) FROM `student_courses_planned` WHERE `user_id` = %s AND `form` = 'form1'", (studentId,))
    if cursor.fetchone()['COUNT(`course_id`)'] == 0:
        flash("Student has not submitted a form1.", "danger")
        myDb.commit()
        cursor.close()
        return redirect(url_for('.index'))
    
    # update form1 status
    cursor.execute("UPDATE `student_info` SET `form_approved` = 1 WHERE `user_id` = %s", (studentId,))

    myDb.commit()
    cursor.close()
    return redirect(url_for('.index'))

@students.route("/advisor", methods=["POST"])
@login_required
@authorize(["gs", "sysadmin"])
def advisor():
    cursor = myDb.cursor(dictionary=True)

    # ensure advisor is selected
    if not request.form["advisorId"]:
        flash("You must select an advisor.", "danger")
        myDb.commit()
        cursor.close()
        return redirect(url_for('.index'))

    # update advisor
    cursor.execute("UPDATE `student_info` SET `advisor_id` = %s WHERE `user_id` = %s", (request.form["advisorId"], request.form["studentId"]))
    flash("Advisor updated.", "success")
    myDb.commit()
    cursor.close()

    return redirect(url_for('.index'))

@students.route("/<int:studentId>/approve/grad")
@login_required
@authorize(["gs", "sysadmin"])
def approve_grad(studentId):
    cursor = myDb.cursor(dictionary=True)

    # check if graduation has been approved 
    cursor.execute("SELECT `grad_status`, `program` FROM `student_info` WHERE `user_id` = %s", (studentId,))
    studentInfo = cursor.fetchone()
    gradStatus = studentInfo['grad_status']
    program = studentInfo['program']

    if gradStatus == 'cleared':
        # if the student has submitted the form and been approved to graduate:
        # 1. Change the student to be of type "alum"
        # 2. Remove the student info stored in the database
        # 3. Remove any planned courses linked to the studnet info. 
        # 4. add the alumni in to the almuni table

        cursor.execute("UPDATE `user` SET `type` = 'alum' WHERE `id` = %s", (studentId,))
        cursor.execute("DELETE FROM `student_info` WHERE `user_id` = %s", (studentId,))
        cursor.execute("DELETE FROM `student_courses_planned` WHERE `user_id` = %s", (studentId,))
        cursor.execute("INSERT INTO `alumni_info` (`user_id`, `program`) VALUES (%s, %s)",(studentId, program))
        
        myDb.commit()
        flash("Student graduated!", "success")
        cursor.close()
        return redirect(url_for('.index'))
    else:
        # graduation has not been approved, so don't clear the student 
        flash("Student has not been cleared to graduate!", "danger")
        myDb.commit()
        cursor.close()
        return redirect(url_for('.index'))


@students.route("/gradDate", methods=["POST"])
@login_required
@authorize(["gs", "sysadmin"])
def gradDate():
    cursor = myDb.cursor(dictionary=True)

    # ensure year and semester are selected and valid
    if not request.form["year"] or not request.form["semester"] or int(request.form["year"]) < 2023 or request.form["semester"] not in ["fall", "spring"]:
        flash("You must provide a valid semester and year..", "danger")
        myDb.commit()
        cursor.close()
        return redirect(url_for('.index'))

    # update advisor
    cursor.execute("UPDATE `student_info` SET `grad_year` = %s, `grad_semester` = %s WHERE `user_id` = %s", (request.form["year"], request.form["semester"], request.form["studentId"]))
    flash("Expected graduation date updated.", "success")
    myDb.commit()
    cursor.close()

    return redirect(url_for('.index'))

@students.route("/advising-form", methods=["GET", "POST"])
@login_required
@authorize(["student"])
def advising_form():
    cursor = myDb.cursor(dictionary=True) 

    # check if student already has submitted advising form
    cursor.execute("SELECT `advising_form_approved` FROM `student_info` WHERE `user_id` = %s", (session['userId'],))
    if cursor.fetchone()['advising_form_approved'] == 1:
        flash("Your advising hold has already been lifted. You do not need to submit an advising form", "info")
        myDb.commit()
        cursor.close()
        return redirect(url_for('index'))
    
    # check if student has already had hold removed
    cursor.execute("SELECT COUNT(`user_id`) FROM `student_courses_planned` WHERE `user_id` = %s AND `form` = 'advising'", (session['userId'],))
    if cursor.fetchone()['COUNT(`user_id`)'] > 0:
        flash("You have already submitted an advising form. Please wait for your advisor to approve it", "info")
        myDb.commit()
        cursor.close()
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        # get form data
        classes = request.form.getlist('class[]')

        for c in classes:
            # check if course already exists in database
            cursor.execute("SELECT `user_id` FROM `student_courses_planned` WHERE `user_id` = %s AND `course_id` = %s AND `form` = 'advising'", (session['userId'], c))
            if cursor.fetchone() is None:
                # add course to database
                cursor.execute("INSERT INTO `student_courses_planned` (`user_id`, `course_id`, `form`) VALUES (%s, %s, 'advising')", (session['userId'], c))
                myDb.commit()
            else:
                # course already exists in database, so delete all courses and return error
                flash("You selected the same course multiple times. Please try again", "warning")
                cursor.execute("DELETE FROM `student_courses_planned` WHERE `user_id` = %s AND `form` = 'advising'", (session['userId'],))
                myDb.commit()
                cursor.close()
                return redirect(url_for('.advising_form'))
        
        flash("Advising form submitted.", "success")
        myDb.commit()
        cursor.close()
        return redirect(url_for('index'))
    
    # get courses from database
    cursor.execute("SELECT `id`, `department`, `course_num`, `title` FROM `course`")
    courses = cursor.fetchall()

    myDb.commit()
    cursor.close()
    return render_template("advising_form.html", courses=courses)

@students.route("/advising-form/<int:studentId>", methods=["GET", "POST"])
@login_required
@authorize(["faculty", "gs", "sysadmin"])
def advising_form_approve(studentId):
    cursor = myDb.cursor(dictionary=True) 

    # ensure advisor is assigned to student
    cursor.execute("SELECT `advising_form_approved`, `advisor_id` FROM `student_info` WHERE `user_id` = %s", (studentId,))
    studentInfo = cursor.fetchone()
    if session['userType'] == "faculty" and studentInfo['advisor_id'] != session['userId']:
        flash("You are not assigned to this student.", "danger")
        myDb.commit()
        cursor.close()
        return redirect(url_for('.index'))

    # get courses from database
    cursor.execute("SELECT `course`.`department`, `course`.`course_num`, `course`.`title` FROM `student_courses_planned` INNER JOIN `course` ON `student_courses_planned`.`course_id` = `course`.`id` WHERE `student_courses_planned`.`user_id` = %s AND `student_courses_planned`.`form` = 'advising'", (studentId,))
    courses = cursor.fetchall()
    if courses == None:
        flash("Student has not submitted an advising form.", "danger")
        myDb.commit()
        cursor.close()
        return redirect(url_for('.index'))

    # get student info
    cursor.execute("SELECT `first_name`, `last_name`, `id` FROM `user` WHERE `id` = %s", (studentId,))
    student = cursor.fetchone()

    if request.method == 'POST':
        # check if student has already had hold removed
        if studentInfo['advising_form_approved'] == 1:
            flash("Student has already had hold removed.", "danger")
            myDb.commit()
            cursor.close()
            return redirect(url_for('.advising_form_approve', studentId=studentId))

        # update database
        cursor.execute("UPDATE `student_info` SET `advising_form_approved` = 1 WHERE `user_id` = %s", (studentId,))
        myDb.commit()

        flash("Advising form approved.", "success")
        cursor.close()
        return redirect(url_for('.advising_form_approve', studentId=studentId))

    myDb.commit()
    cursor.close()
    return render_template("advising_form_approve.html",
                           student = student,
                           courses = courses,
                           approved = studentInfo['advising_form_approved'])