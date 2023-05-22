from flask import Flask, render_template, session, redirect, url_for, request, flash
from ads import ads, able_to_graduate
from helpers import login_required, myDb
from students import programTypes
from apps import apps, appIncomplete
from reports import reports
from regs import regs
from chat import chat

app = Flask(__name__)
app.secret_key = "eot"
app.register_blueprint(ads, url_prefix='/ads')
app.register_blueprint(apps, url_prefix='/apps')
app.register_blueprint(regs, url_prefix="/regs")
app.register_blueprint(reports, url_prefix="/reports")
app.register_blueprint(chat, url_prefix="/chat")

@app.route('/')
@login_required
def index():
    cursor = myDb.cursor(dictionary=True)
    userId = session['userId']

    #Get the requested user. 
    cursor.execute("SELECT `first_name`, `last_name`, `type` FROM user WHERE id = %s", (userId,))
    user = cursor.fetchone()
    session['userType'] = user['type']

    # Redirect to login if user is not found
    if user == None:
        myDb.commit()
        cursor.close()
        return redirect(url_for("login"))

    #Show the student home view if user if of type student 
    if user["type"] == "student":
        # Check if the student has filled out form 1
        cursor.execute("SELECT COUNT(`course_id`) FROM `student_courses_planned` WHERE `user_id` = %s", (userId,))
        form1 = cursor.fetchone()['COUNT(`course_id`)'] > 0

        # Check if the student has an approved advising form
        cursor.execute("SELECT `advising_form_approved` FROM `student_info` WHERE `user_id` = %s", (userId,))
        advising_form_approved = cursor.fetchone()['advising_form_approved']

        # Check if the student has filled out advising form
        cursor.execute("SELECT COUNT(`course_id`) FROM `student_courses_planned` WHERE `user_id` = %s AND `form` = 'advising'", (userId,))
        advising_form = cursor.fetchone()['COUNT(`course_id`)'] > 0
        myDb.commit()
        cursor.close()

        return render_template("dashboard.html",
                               user = user,
                               form1 = form1, able_to_graduate = able_to_graduate(userId),
                               advising_form_approved = advising_form_approved,
                               advising_form = advising_form,)

    #Show the alum home view if user is of type alum 
    if user["type"] == "alum":
        cursor.execute("SELECT `program`, `grad_year` FROM `alumni_info` WHERE `user_id` = %s", (userId,))
        alum_info = cursor.fetchone()
        myDb.commit()
        cursor.close()
        return render_template("dashboard.html", user=user, alum_info=alum_info, programTypes=programTypes)
        
    #Show the faculty advisor view if user is of type faculty advisor 
    if user["type"] == "faculty":
        cursor.execute("SELECT `is_advisor`, `is_reviewer`, `is_instructor`, `is_admissions_chair` FROM `faculty_info` WHERE `user_id` = %s", (userId,))
        faculty_info = cursor.fetchone()
        myDb.commit()
        cursor.close()
        return render_template("dashboard.html", user=user, faculty=faculty_info)
    
    # Applicant home view
    if user["type"] == "applicant":
        # Get materials needed
        materials = appIncomplete(session["userId"])

        # Get application status
        appStatus = None
        cursor.execute("SELECT appStatus FROM applicant WHERE university_id = %s", (session["userId"],))
        result = cursor.fetchone()
        if cursor.rowcount > 0:
            appStatus = result["appStatus"]

        # Check if an application has been submitted
        cursor.execute("SELECT university_id, transcriptStatus, r1status, r2status, r3status FROM applicationForm WHERE university_id = %s", (session["userId"],))
        result = cursor.fetchone()
        appSubmitted = cursor.rowcount > 0
        
        myDb.commit()
        cursor.close()
        return render_template("dashboard.html", user=user, appStatus=appStatus, appSubmitted=appSubmitted, materialsNeeded=materials)

    return render_template("dashboard.html", user=user)

@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':    
        cursor = myDb.cursor(dictionary=True)
        cursor.execute("SELECT `id`, `type`, `username`, `password` FROM user WHERE username=%s and password=%s", (request.form['username'],request.form['password']))

        user = cursor.fetchone()
        
        if user == None:
            flash("User/password is incorrect. Please try again.", "warning")
            myDb.commit()
            cursor.close()
            return render_template('login.html')

        session['userId'] = user['id']
        session['id'] = user['id']
        session['username'] = user['username']
        session['userType'] = user['type']
        session['type'] = user['type']
        session['registration'] = []

        myDb.commit()
        cursor.close()
        if 'next' in session:
            return redirect(session.pop('next', None))
        
        return redirect(url_for("index"))

    return render_template('login.html')

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

@app.route("/create_acc_page")
def create_acc_page():
    if 'userId' not in session:
        return render_template("create_account.html")
    else:
        return redirect(url_for('login'))

@app.route("/create_acc", methods=['GET', 'POST'])
def create_acc():

    cursor = myDb.cursor(dictionary=True) 
    if request.method == 'POST':
        cursor.execute("SELECT username FROM user WHERE username=%s", (request.form["userName"],))
        name = cursor.fetchone()
        if name == None:
            
            cursor.execute("INSERT INTO `user` (`type`, `email`, `username`, `password`, `first_name`,`last_name`, `street_address`, `city`, `state`, `zip`) VALUES (%s, %s,%s, %s, %s, %s, %s, %s, %s, %s)", ("applicant", request.form['email'], request.form['userName'], request.form['pass'], request.form['firstName'], request.form['lastName'], request.form['streetAdd'], request.form['city'], request.form['state'], request.form['zip'] ))
            myDb.commit()
            cursor.execute("SELECT id FROM user WHERE username=%s", (request.form["userName"],))
            id = cursor.fetchone()
            # print (id)
            # print (id['id'])
            university_id = id['id']
            # insert data into applicant table
            # assume everyone making an account is an applicant

            appStatus = "Incomplete"
            mail_transcript = "No"

            appStatus = "Pending"

            ssn = request.form["ssn"]
            username = request.form["userName"]
            cursor.execute("INSERT INTO applicant (ssn, appStatus, university_id, mail_transcript) VALUES (%s, %s, %s, %s)",
            (ssn, appStatus, university_id, mail_transcript,))
            myDb.commit()
            cursor.close()
            flash("You have successfully created your account! Please sign in.", "success")
            return redirect(url_for('login'))
        
        flash("This username already exists. Please choose a different one.", "danger")
        myDb.commit()
        cursor.close()
        return redirect(url_for('create_acc_page'))

@app.errorhandler(401)
def forbidden(e):
    return render_template('401.html')
