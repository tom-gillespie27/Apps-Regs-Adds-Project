from flask import render_template, request, redirect, url_for, flash, Blueprint, session
from helpers import authorize, myDb, login_required

transcript = Blueprint('transcript', __name__, template_folder='templates')

gradeConversion = {
    "A": 4.0,
    "A-": 3.7,
    "B+": 3.3,
    "B": 3.0,
    "B-": 2.7,
    "C+": 2.3,
    "C": 2.0,
    "F": 0.0
}

def calculateGpa(studentId, semester = None):
    cursor = myDb.cursor(dictionary=True)
    if semester is None:
        cursor.execute("SELECT `grade`, `credits` FROM `student_courses` INNER JOIN `course` ON `student_courses`.`course_id` = `course`.`id` WHERE `user_id` = %s", (studentId,))
    else:
        cursor.execute("SELECT `grade`, `credits` FROM `student_courses` INNER JOIN `course` ON `student_courses`.`course_id` = `course`.`id` WHERE `user_id` = %s AND `semester` = %s AND `year` = %s", (studentId, semester["semester"], semester["year"]))
    courses = cursor.fetchall()
    if len(courses) == 0:
        myDb.commit()
        cursor.close()
        return None
    myDb.commit()

    totalCredits = 0
    totalGradePoints = 0
    for course in courses:
        if course["grade"] not in gradeConversion:
            continue
        totalCredits += course["credits"]
        totalGradePoints += course["credits"] * gradeConversion[course["grade"]]

    if totalCredits == 0:
        cursor.close()
        return None
    
    cursor.close()
    return round(totalGradePoints / totalCredits, 2)

def studentSuspended(studentId):
    cursor = myDb.cursor(dictionary=True)
    cursor.execute("SELECT COUNT(`grade`) AS `count` FROM `student_courses` WHERE `user_id` = %s AND `grade` NOT IN ('A', 'A-', 'B+', 'B', 'IP')", (studentId,))
    result = cursor.fetchone()
    myDb.commit()
    cursor.close()
    return result["count"] >= 3

@transcript.route("/")
@transcript.route("/<int:userId>")
@login_required
def view(userId=None):    
    # Create a cursor to execute queries
    cursor = myDb.cursor(dictionary=True)
    
    # If userId is not specified, use the currently logged in user's id
    if userId is None:
        userId = session['userId']

    # Get requested user
    cursor.execute("SELECT `first_name`, `last_name`, `type` FROM user WHERE id = %s", (userId,))
    user = cursor.fetchone()

    if user is None:
        flash("Requested user does not exist.", "danger")

        myDb.commit()
        cursor.close()
        return redirect(url_for('index'))

    # Check if the user requested is a student/alum
    if not user or user["type"] not in ("student", "alum"):
        # If the user is not a student/alum, redirect to the home page
        flash("Requested user is not a student and does not have a transcript.", "danger")

        myDb.commit()
        cursor.close()
        return redirect(url_for('ads.home'))
    
    # If the logged in user is faculty, ensure they are allowed to view the requested student's transcript
    if session['userType'] == "faculty":
        cursor.execute("SELECT `advisor_id` FROM `student_info` WHERE `user_id` = %s AND `advisor_id` = %s", (userId, session['userId']))
        advises = cursor.fetchone()
        
        # check if faculty teaches any courses that the student has taken
        cursor.execute("SELECT COUNT(*) AS `count` FROM `student_courses` INNER JOIN `sections` ON (`student_courses`.`course_id` = `sections`.`course_id` AND `student_courses`.`semester` = `sections`.`csem` AND `student_courses`.`year` = `sections`.`cyear`) WHERE `user_id` = %s AND `fid` = %s", (userId, session['userId']))
        teaches = cursor.fetchone()
        if teaches["count"] == 0 and advises is None:
            flash("You are not allowed to view the requested student's transcript.", "danger")

            myDb.commit()
            cursor.close()
            return redirect(url_for('ads.home'))

    # If the logged in user is a student, ensure they are allowed to only view their own transcript
    elif session['userType'] in ("student", "alum"):
        if session['userId'] != userId:
            flash("You are not allowed to view the requested student's transcript.", "danger")

            myDb.commit()
            cursor.close()
            return redirect(url_for('.view'))

    # Get the semesters the user has taken courses in
    cursor.execute("SELECT DISTINCT `semester`, `year` FROM `student_courses` WHERE `user_id` = %s ORDER BY `year` DESC, `semester` DESC", (userId,))
    semesters = cursor.fetchall()

    # Get the courses the user has taken in each semester
    for semester in semesters:
        cursor.execute("SELECT `department`, `course_num`, `title`, `credits`, `grade` FROM `student_courses` INNER JOIN `course` ON `student_courses`.`course_id` = `course`.`id` WHERE `user_id` = %s AND `semester` = %s AND `year` = %s", (userId, semester["semester"], semester["year"]))
        semester["courses"] = cursor.fetchall()
        semester["gpa"] = calculateGpa(userId, semester)

    myDb.commit()

    # Calculate the student's overall GPA
    overallGpa = calculateGpa(userId)
    cursor.close()
    
    return render_template("transcript.html", semesters=semesters, overallGpa=overallGpa, suspended=studentSuspended(userId), user=user)
