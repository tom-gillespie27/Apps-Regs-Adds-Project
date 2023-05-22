from flask import render_template, request, redirect, url_for, flash, Blueprint
from helpers import authorize, myDb, login_required

users = Blueprint('users', __name__, template_folder='templates')

def validate_user(user):
    if user['firstName'] == "" or user['lastName'] == "" or user['userType'] == "" or user['stAddr'] == "" or user['city'] == "" or user['state'] == "" or user['zipCode'] == "" or user['email'] == "" or user['bday'] == "" or\
        (user['userType'] == "student" and user['advisorId'] == "") or\
        (user['userType'] == "student" and user['program'] == "") or\
        (user['userType'] == "alum" and user['program'] == "") or\
        (user['userType'] == "applicant" and user['ssn'] == "") or\
        (user['userType'] == "faculty" and user['department'] == ""):
        # If any of the required fields are empty, return False
        return False
    if user['userType'] not in userTypes:
        # If the user type is not valid, return False
        return False
    if len(user['firstName']) > 50 or len(user['lastName']) > 50:
        # If the first or last name is too long, return False
        return False

    if len(user['stAddr']) > 50 or len(user['city']) > 50:
        #If the street address or city is too long 
        return False
    
    if len(user['state']) != 2:
        #If the state is too short or too long
        return False
    
    if len(user['zipCode']) != 5 or not user['zipCode'].isnumeric():
        return False 

    if user['userType'] == "student":
        # If the user is a student, ensure the advisor exists
        cursor = myDb.cursor(dictionary=True)
        cursor.execute("SELECT `id` FROM `user` WHERE `id` = %s AND `type` = 'faculty'", (user['advisorId'],))
        if cursor.fetchone() is None:
            return False
        
    if user['userType'] == "applicant" and (len(user['ssn']) != 9 or not user['ssn'].isnumeric()):
        # If the user is an applicant, ensure the SSN is valid
        return False

    return True

userTypes = {
    "alum": "Alumni",
    "applicant": "Applicant",
    "faculty": "Faculty",
    "gs": "Grad Secretary",
    "registrar": "Registrar",
    "student": "Student",
    "sysadmin": "Systems Administrator"
}

@users.route("/")
@login_required
@authorize(["sysadmin"])
def index():
    global userTypes
    cursor = myDb.cursor(dictionary=True)

    cursor.execute("SELECT `id`, `first_name`, `last_name`, `type` FROM `user`")
    users = cursor.fetchall()
    myDb.commit()
    cursor.close()

    return render_template("user_index.html", users=users, userTypes=userTypes)

@users.route("/<int:userId>/edit", methods=["GET", "POST"])
@login_required
@authorize(["sysadmin"])
def edit(userId):
    global userTypes
    cursor = myDb.cursor(dictionary=True)

    # Ensure the user exists
    cursor.execute("SELECT `id`, `first_name`, `last_name`, `type`, `email`, `bday`, `street_address`, `city`, `state`, `zip` FROM `user` WHERE `id` = %s", (userId,))
    user = cursor.fetchone()
    if user is None:
        flash("The requested user does not exist.")
        myDb.commit()
        cursor.close()
        return redirect(url_for('.index'))

    if request.method == "POST":
        # Get the form data
        firstName = request.form["firstName"]
        lastName = request.form["lastName"]
        userType = request.form["userType"]
        advisorId = request.form["advisorId"] if "advisorId" in request.form else ""
        stAddr = request.form["stAddr"]
        city = request.form["city"]
        state = request.form["state"]
        zipCode = request.form["zipCode"]
        email = request.form["email"]
        bday = request.form["bday"]
        program = request.form["program"] if "program" in request.form else ""
        ssn = request.form["ssn"] if "ssn" in request.form else ""
        department = request.form["department"] if "department" in request.form else ""
        isAdvisor = request.form["isAdvisor"] if "isAdvisor" in request.form else ""
        isReviewer = request.form["isReviewer"] if "isReviewer" in request.form else ""
        isInstructor = request.form["isInstructor"] if "isInstructor" in request.form else ""
        isAdmissionsChair = request.form["isAdmissionsChair"] if "isAdmissionsChair" in request.form else ""

        # Validate the form data
        validated = validate_user(request.form)

        if validated:
            # Update the user in the database
            cursor.execute("UPDATE `user` SET `first_name` = %s, `last_name` = %s, `type` = %s, `street_address` = %s, `city` = %s, `state` = %s, `zip` = %s, `email` = %s, `bday` = %s WHERE `id` = %s", (firstName, lastName, userType, stAddr, city, state, zipCode, email, bday, userId))
            if userType == "student":
                # If the user is a student, update their student info
                cursor.execute("UPDATE `student_info` SET `advisor_id` = %s, `program` = %s WHERE `user_id` = %s", (advisorId, program, userId))
            elif userType == "alum":
                # If the user is an alumni, update their alumni info
                cursor.execute("UPDATE `alumni_info` SET `program` = %s WHERE `user_id` = %s", (program, userId))
            elif userType == "applicant":
                # If the user is an applicant, update their applicant info
                cursor.execute("UPDATE `applicant` SET `ssn` = %s WHERE `university_id` = %s", (ssn, userId))
            elif userType == "faculty":
                # If the user is a faculty member, update their faculty info
                cursor.execute("UPDATE `faculty_info` SET `department` = %s, `is_advisor` = %s, `is_reviewer` = %s, `is_instructor` = %s, `is_admissions_chair` = %s WHERE `user_id` = %s", (department, isAdvisor, isReviewer, isInstructor, isAdmissionsChair, userId))

            myDb.commit()
            cursor.close()
            # Redirect to the user index page
            return redirect(url_for('.index'))
    
    # get departments
    cursor.execute("SELECT DISTINCT `department` FROM `course`")
    departments = cursor.fetchall()

    # If the user is a student, get their student info
    if user['type'] == "student":
        cursor.execute("SELECT `advisor_id`, `program` FROM `student_info` WHERE `user_id` = %s", (userId,))
        studentInfo = cursor.fetchone()
        user['advisor_id'] = studentInfo['advisor_id']
        user['program'] = studentInfo['program']
    elif user['type'] == "alum":
        cursor.execute("SELECT `program` FROM `alumni_info` WHERE `user_id` = %s", (userId,))
        alumniInfo = cursor.fetchone()
        user['program'] = alumniInfo['program']
    elif user['type'] == "applicant":
        cursor.execute("SELECT `ssn` FROM `applicant` WHERE `university_id` = %s", (userId,))
        applicantInfo = cursor.fetchone()
        user['ssn'] = applicantInfo['ssn']
    elif user['type'] == "faculty":
        cursor.execute("SELECT `department`, `is_advisor`, `is_reviewer`, `is_instructor`, `is_admissions_chair` FROM `faculty_info` WHERE `user_id` = %s", (userId,))
        facultyInfo = cursor.fetchone()
        user['department'] = facultyInfo['department']
        user['is_advisor'] = facultyInfo['is_advisor']
        user['is_reviewer'] = facultyInfo['is_reviewer']
        user['is_instructor'] = facultyInfo['is_instructor']
        user['is_admissions_chair'] = facultyInfo['is_admissions_chair']
    
    # Get the list of faculty advisors
    cursor.execute("SELECT `id`, `first_name`, `last_name` FROM `faculty_info` INNER JOIN `user` ON `user`.`id` = `faculty_info`.`user_id` WHERE `is_advisor` = 1")
    advisors = cursor.fetchall()

    myDb.commit()
    cursor.close()

    return render_template("user_edit.html", userTypes=userTypes, user=user, advisors=advisors, departments = departments)

@users.route("/add", methods=["GET", "POST"])
@login_required
@authorize(["sysadmin"])
def add():
    global userTypes
    cursor = myDb.cursor(dictionary=True)

    if request.method == "POST":
        # Get the form data
        firstName = request.form["firstName"]
        lastName = request.form["lastName"]
        userType = request.form["userType"]
        advisorId = request.form["advisorId"] if "advisorId" in request.form else ""
        stAddr = request.form["stAddr"]
        city = request.form["city"]
        state = request.form["state"]
        zipCode = request.form["zipCode"]
        email = request.form["email"]
        username = request.form["username"]
        password = request.form["password"]
        bday = request.form["bday"]
        program = request.form["program"] if "program" in request.form else ""
        ssn = request.form["ssn"] if "ssn" in request.form else ""
        department = request.form["department"] if "department" in request.form else ""
        isAdvisor = request.form["isAdvisor"] if "isAdvisor" in request.form else ""
        isReviewer = request.form["isReviewer"] if "isReviewer" in request.form else ""
        isInstructor = request.form["isInstructor"] if "isInstructor" in request.form else ""
        isAdmissionsChair = request.form["isAdmissionsChair"] if "isAdmissionsChair" in request.form else ""

        # Validate the form data
        validated = validate_user(request.form)

        if validated:
            # Insert the user into the database
            cursor.execute("INSERT INTO `user` (`first_name`, `last_name`, `type`, `street_address`, `city`, `state`, `zip`, `email`, `username`, `password`, `bday`) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", (firstName, lastName, userType, stAddr, city, state, zipCode, email, username, password, bday))
            if userType == "student":
                userId = cursor.lastrowid
                cursor.execute("INSERT INTO `student_info` (`user_id`, `advisor_id`, `program`) VALUES (%s, %s, %s)", (userId, advisorId, program))
            elif userType == "alum":
                userId = cursor.lastrowid
                cursor.execute("INSERT INTO `alumni_info` (`user_id`, `program`) VALUES (%s, %s)", (userId, program))
            elif userType == "applicant":
                userId = cursor.lastrowid
                cursor.execute("INSERT INTO `applicant` (`university_id`, `appStatus`, `ssn`) VALUES (%s, %s, %s)",(userId, "Pending", ssn))
            elif userType == "faculty":
                userId = cursor.lastrowid
                cursor.execute("INSERT INTO `faculty_info` (`user_id`, `department`, `is_advisor`, `is_reviewer`, `is_instructor`, `is_admissions_chair`) VALUES (%s, %s, %s, %s, %s, %s)", (userId, department, isAdvisor, isReviewer, isInstructor, isAdmissionsChair))

            myDb.commit()
            cursor.close()
            # Redirect to the user index page
            return redirect(url_for('.index'))

    # Get the list of faculty advisors
    cursor.execute("SELECT `id`, `first_name`, `last_name` FROM `faculty_info` INNER JOIN `user` ON `user`.`id` = `faculty_info`.`user_id` WHERE `is_advisor` = 1")
    advisors = cursor.fetchall()
    
    # get departments
    cursor.execute("SELECT DISTINCT `department` FROM `course`")
    departments = cursor.fetchall()

    myDb.commit()
    cursor.close()

    return render_template("user_add.html", userTypes=userTypes, advisors=advisors, departments = departments)

@users.route("/<int:userId>/remove")
@login_required
@authorize(["sysadmin"])
def remove(userId):
    cursor = myDb.cursor(dictionary=True)

    # Ensure the user exists
    cursor.execute("SELECT `id`, `type` FROM `user` WHERE `id` = %s", (userId,))
    user = cursor.fetchone()
    if user is None:
        flash("The requested user does not exist.")

        myDb.commit()
        cursor.close()
        return redirect(url_for('.index'))

    # Remove the user from the database
    cursor.execute("DELETE FROM `user` WHERE `id` = %s", (userId,))
    if user['type'] == "student":
        cursor.execute("DELETE FROM `student_info` WHERE `user_id` = %s", (userId,))
        cursor.execute("DELETE FROM `student_courses` WHERE `user_id` = %s", (userId,))
        cursor.execute("DELETE FROM `student_courses_planned` WHERE `user_id` = %s", (userId,))
    elif user['type'] == "alum":
        cursor.execute("DELETE FROM `alumni_info` WHERE `user_id` = %s", (userId,))
        cursor.execute("DELETE FROM `alumni_chat_messages` WHERE `user_id` = %s", (userId,))
    elif user['type'] == "applicant":
        cursor.execute("DELETE FROM `applicant` WHERE `university_id` = %s", (userId,))
        cursor.execute("DELETE FROM `applicationForm` WHERE `university_id` = %s", (userId,))
        cursor.execute("DELETE FROM `reviewForm` WHERE `university_id` = %s", (userId,))
    elif user['type'] == "faculty":
        cursor.execute("DELETE FROM `faculty_info` WHERE `user_id` = %s", (userId,))
    myDb.commit()
    cursor.close()
    flash("User successfully removed.", "success")
    return redirect(url_for('.index'))
