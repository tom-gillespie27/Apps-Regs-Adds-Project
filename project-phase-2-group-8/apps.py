from flask import session, render_template, request, redirect, Blueprint, url_for, flash, abort, send_file
from helpers import myDb, login_required, authorize
from random import randint
from io import BytesIO

apps = Blueprint('apps', __name__, template_folder='templates/apps')

# returns a list of materials needed for an application, and updates appStatus to complete if all materials have been received
def appIncomplete(university_id):
    cursor = myDb.cursor(dictionary = True)

    materialsNeeded = [] # list of materials needed

    # Check if an application has been submitted
    cursor.execute("SELECT transcriptStatus, r1status, r2status, r3status FROM applicationForm WHERE university_id = %s", (university_id,))
    result = cursor.fetchone()
    if result == None:
        # No application has been submitted
        materialsNeeded.append('Application')
        myDb.commit()
        cursor.close()
        return materialsNeeded

    # Get materials needed
    if result['transcriptStatus'] == 'Not Received':
        materialsNeeded.append('Transcript')
    if result['r1status'] == 'Not Received':
        materialsNeeded.append('Recommendation Letter 1')
    if result['r2status'] == 'Not Received':
        materialsNeeded.append('Recommendation Letter 2')
    if result['r3status'] == 'Not Received':
        materialsNeeded.append('Recommendation Letter 3')

    # if no materials needed, update appStatus to complete
    if len(materialsNeeded) == 0:
        cursor.execute("SELECT appStatus FROM applicant WHERE university_id = %s AND appStatus = 'Incomplete'", (university_id,))
        result = cursor.fetchone()
        if cursor.rowcount > 0:
            # update appStatus to complete, only if it is currently incomplete
            cursor.execute("UPDATE applicant SET appStatus = 'Complete' WHERE university_id = %s", (university_id,))
            myDb.commit()

    myDb.commit()
    cursor.close()
    return materialsNeeded

@apps.route('/createAccount', methods=['GET', 'POST'])
def createAccount():
    cursor = myDb.cursor(dictionary = True)

    if request.method == 'POST':
    # fields for applicant
        username = request.form["username"]
        session['username'] = username
        password = request.form["userpass"]
        email = request.form["email"]
        ssn = int(request.form["ssn"])
        first_name = request.form["first_name"]
        last_name = request.form["last_name"]
        bday = request.form["bday"]
        type = request.form["type"]

        # assumes that only applicants are creating an account
        #userType = request.form["userType"]

        # insert relevent data into users table
        
        cursor.execute(
            "INSERT INTO user (username, password, email, first_name, last_name, bday, type) VALUES(%s,%s,%s,%s,%s,%s,%s)",
            (username, password, email, first_name, last_name, bday, type,))
        myDb.commit()
        # insert relevent data into applicant table
        # use random # generator to generate a university_id
        #university_id = randint(100000000, 999999999)
        
        # randint is inclusive at both ends
        # set app status to false
        appStatus = "Incomplete"
        # insert into the applicants table
        cursor.execute(
            "SELECT id FROM user WHERE username = %s", (username,)
        )
        university_id = cursor.fetchone()
        university_id = university_id['id']
        session['university_id'] = university_id
        cursor.execute(
            "INSERT INTO applicant (appStatus, ssn, university_id) VALUES(%s,%s,%s)",
            (appStatus, ssn, university_id))
        myDb.commit()
        cursor.close()
        return redirect(url_for('login'))
    elif request.method == 'GET':
        myDb.commit()
        cursor.close()
        return render_template('createAccount.html')
    myDb.commit()
    cursor.close()
    return redirect("/")

@apps.route('/app-status/update', methods=['POST'])
@login_required
@authorize(['faculty', 'gs', 'sysadmin'])
def update_app_status():
    cursor = myDb.cursor(dictionary = True)
    cursor.execute("UPDATE applicant SET appStatus = %s WHERE university_id = %s", (request.form["status"],request.form["id"]))

    myDb.commit()

    flash("Application status updated successfully", "success")

    appIncomplete(request.form['id']) # check if app is complete now

    myDb.commit()
    cursor.close()
    return redirect(url_for('.applicants'))

@apps.route('/transcript-status/update', methods=['POST'])
@login_required
@authorize(['gs', 'sysadmin', "faculty"])
def update_transcript_status():
    cursor = myDb.cursor(dictionary = True)
    
    # check if faculty is chair
    if session['userType'] == 'faculty':
        cursor.execute("SELECT `is_admissions_chair` FROM `faculty_info` WHERE `user_id` = %s", (session['userId'],))
        result = cursor.fetchone()
        if result['is_admissions_chair'] == 0:
            # not chair, abort
            myDb.commit()
            cursor.close()
            abort(401)

    cursor.execute("UPDATE applicationForm SET transcriptStatus = %s WHERE university_id = %s", (request.form["status"], request.form["id"]))
    myDb.commit()

    flash("Transcript status updated successfully", "success")
    
    appIncomplete(request.form['id']) # check if app is complete now

    if 'student' in request.form:
        # if from an application, redirect back to the application
        myDb.commit()
        cursor.close()
        return redirect(url_for('.viewApplication', university_id=request.form["student"]))

    myDb.commit()
    cursor.close()
    return redirect(url_for('.applicants'))

@apps.route('/email/<int:university_id>')
@login_required
@authorize(["applicant", "gs", "sysadmin", "faculty"])
def email(university_id):
    # get the user's name
    cursor = myDb.cursor(dictionary = True)
    cursor.execute("SELECT id, first_name, last_name FROM user WHERE id = %s", (university_id,))
    student = cursor.fetchone()

    myDb.commit()
    cursor.close()
    return render_template("email.html", student=student)

@apps.route('/applicants')
@login_required
@authorize(["gs", "faculty", "sysadmin"])
def applicants():
    cursor = myDb.cursor(dictionary = True)

    facultyType = {
        "advisor": False,
        "instructor": False,
        "reviewer": False,
        "admissions_chair": False
    }
    if session['userType'] == 'faculty':
        # get faculty type
        cursor.execute("SELECT `is_advisor`, `is_reviewer`, `is_instructor`, `is_admissions_chair` FROM `faculty_info` WHERE `user_id` = %s", (session['userId'],))
        faculty_info = cursor.fetchone()
        facultyType['advisor'] = faculty_info['is_advisor']
        facultyType['instructor'] = faculty_info['is_instructor']
        facultyType['reviewer'] = faculty_info['is_reviewer']
        facultyType['admissions_chair'] = faculty_info['is_admissions_chair']
        if not facultyType['reviewer'] and not facultyType['admissions_chair'] and not facultyType['advisor']:
            myDb.commit()
            cursor.close()
            abort(401) # unauthorized

    admitDate = request.args.get('admitDate')
    degree = request.args.get('degree')
    status = request.args.get('status')

    query = "SELECT applicant.*, user.first_name, user.last_name, applicationForm.degreeSeeking FROM applicant INNER JOIN user ON applicant.university_id = user.id LEFT JOIN applicationForm ON applicant.university_id = applicationForm.university_id WHERE appStatus != 'Matriculated'"
    params = []
    if admitDate != None and admitDate != "":
        query += " AND `startDate` = %s"
        params.append(admitDate)
    if degree != None and degree != "":
        query += " AND `degreeSeeking` = %s"
        params.append(degree)
    if status != None and status != "":
        query += " AND `appStatus` LIKE 'Admit%'"

    cursor.execute(query, params)
    applicants = cursor.fetchall()

    for applicant in applicants:
        cursor.execute("SELECT * FROM applicationForm WHERE university_id = %s", (applicant["university_id"],))
        form = cursor.fetchone()
        applicant["form"] = True if form else False
        applicant["app"] = form

    # get advisors
    cursor.execute("SELECT user.id, user.first_name, user.last_name FROM user INNER JOIN faculty_info ON user.id = faculty_info.user_id WHERE faculty_info.is_advisor = 1")
    advisors = cursor.fetchall()
    
    myDb.commit()
    cursor.close()
    return render_template("applicants.html", applicants = applicants, facultyType = facultyType, advisors = advisors)

@apps.route('/viewApplication/<university_id>', methods=['GET','POST'])
@login_required
@authorize(["gs", "sysadmin", "faculty"])
def viewApplication(university_id):
    cursor = myDb.cursor(dictionary = True)

    # check if faculty is authorized to fill out review form
    cursor.execute("SELECT * FROM faculty_info WHERE user_id = %s", (session['userId'],))
    faculty_info = cursor.fetchone()

    if session['userType'] == 'faculty' and not faculty_info['is_advisor'] and not faculty_info['is_admissions_chair'] and not faculty_info['is_reviewer']:
        flash("You are not authorized to view applications.", "danger")
        myDb.commit()
        cursor.close()
        return redirect(url_for('.applicants'))
    
    cursor.execute("SELECT * FROM applicationForm INNER JOIN applicant ON applicant.university_id = applicationForm.university_id WHERE applicationForm.university_id = %s", (university_id,))
    form = cursor.fetchone()

    # get the user's name
    cursor = myDb.cursor(dictionary = True)
    cursor.execute("SELECT id, first_name, last_name FROM user WHERE id = %s", (university_id,))
    student = cursor.fetchone()
    # see if they are mailing it in
    cursor.execute("SELECT mail_transcript FROM applicant WHERE university_id = %s", (university_id,))
    mail_transcript = cursor.fetchone()
    mail_transcript = mail_transcript['mail_transcript']
    # see if they have uploaded the transcript
    cursor.execute("SELECT file_name FROM transcript WHERE trans_id = %s", (university_id,))
    transcript = cursor.fetchone()
    upload= "No"
    if transcript != None:
        upload = "Applicant's transcript has been uploaded"
    myDb.commit()
    cursor.close()
    return render_template("viewApplication.html", form = form, student = student, faculty_info = faculty_info, mail_transcript = mail_transcript, upload = upload)

@apps.route('/viewReviewForm/<university_id>', methods=['GET','POST'])
@login_required
@authorize(["gs", "sysadmin", "faculty"])
def viewReviewForm(university_id):
    cursor = myDb.cursor(dictionary = True)

    # check if faculty is authorized to fill out review form
    cursor.execute("SELECT * FROM faculty_info WHERE user_id = %s", (session['userId'],))
    faculty_info = cursor.fetchone()

    if session['userType'] == 'faculty' and not faculty_info['is_admissions_chair'] and not faculty_info['is_reviewer'] and not faculty_info['is_advisor']:
        flash("You are not authorized to view review forms.", "danger")
        myDb.commit()
        cursor.close()
        return redirect(url_for('.applicants'))
    
    # check if application is complete
    appIncomplete(university_id)
    cursor.execute("SELECT appStatus FROM applicant WHERE university_id = %s", (university_id,))
    appStatus = cursor.fetchone()['appStatus']
    if appStatus in ["Pending", "Incomplete"]:
        flash("The application is not complete. You cannot submit a review form until it's complete.", "danger")
        myDb.commit()
        cursor.close()
        return redirect(url_for('.applicants'))
    
    cursor.execute("SELECT reviewForm.*, first_name, last_name FROM reviewForm INNER JOIN user ON reviewForm.reviewer = user.id WHERE university_id = %s", (university_id,))
    form = cursor.fetchall()
    
    # get advisors
    cursor.execute("SELECT user.id, user.first_name, user.last_name FROM user INNER JOIN faculty_info ON user.id = faculty_info.user_id WHERE faculty_info.is_advisor = 1")
    advisors = cursor.fetchall()

    # get average ratings for each recommendation
    cursor.execute("SELECT AVG(r1rating) AS r1, AVG(r2rating) AS r2, AVG(r3rating) AS r3 FROM reviewForm WHERE university_id = %s", (university_id,))
    averages = cursor.fetchone()
    
    # count credible reviews
    cursor.execute("SELECT SUM(r1credible) AS r1, SUM(r2credible) AS r2, SUM(r3credible) AS r3 FROM reviewForm WHERE university_id = %s", (university_id,))
    credible = cursor.fetchone()
    
    # count generic reviews
    cursor.execute("SELECT SUM(r1generic) AS r1, SUM(r2generic) AS r2, SUM(r3generic) AS r3 FROM reviewForm WHERE university_id = %s", (university_id,))
    generic = cursor.fetchone()

    # get student name
    cursor.execute("SELECT first_name, last_name FROM user WHERE id = %s", (university_id,))
    student = cursor.fetchone()
    myDb.commit()
    cursor.close()

    return render_template("viewReviewForm.html", forms=form, studentId = university_id, advisors = advisors, averages=averages, credible=credible, generic=generic, facultyType = faculty_info, appStatus = appStatus, student = student)

@apps.route('/fillReviewForm')
@apps.route('/fillReviewForm/<int:university_id>')
@login_required
@authorize(["faculty", "sysadmin",])
def fillReviewForm(university_id = None):
    # check if faculty is authorized to fill out review form
    cursor = myDb.cursor(dictionary = True)
    cursor.execute("SELECT * FROM faculty_info WHERE user_id = %s", (session['userId'],))
    faculty_info = cursor.fetchone()

    if session['userType'] == 'faculty' and not faculty_info['is_reviewer'] and not faculty_info['is_admissions_chair']:
        flash("You are not authorized to fill out review forms.", "danger")
        myDb.commit()
        cursor.close()
        return redirect(url_for('.applicants'))
    
    # check if application is complete
    appIncomplete(university_id)
    cursor.execute("SELECT appStatus FROM applicant WHERE university_id = %s", (university_id,))
    appStatus = cursor.fetchone()['appStatus']
    if appStatus not in ["Complete", "Under Review"]:
        flash("The application is not complete. You cannot submit a review form until it's complete.", "danger")
        myDb.commit()
        cursor.close()
        return redirect(url_for('.applicants'))
    
    # check if review form has already been submitted by this user
    cursor.execute("SELECT * FROM reviewForm WHERE university_id = %s AND reviewer = %s", (university_id, session['userId']))
    if cursor.fetchone():
        flash("You have already submitted a review form for this applicant.", "danger")
        myDb.commit()
        cursor.close()
        return redirect(url_for('.applicants'))
    
    # get advisors
    cursor.execute("SELECT user.id, user.first_name, user.last_name FROM user INNER JOIN faculty_info ON user.id = faculty_info.user_id WHERE faculty_info.is_advisor = 1")
    advisors = cursor.fetchall()

    # get semester applied
    cursor.execute("SELECT startDate, r1letter, r2letter, r3letter, r1affiliation, r2affiliation, r3affiliation, r1writer, r2writer, r3writer, r1title, r2title, r3title FROM applicationForm WHERE university_id = %s", (university_id,))
    appForm = cursor.fetchone()

    # get student name
    cursor.execute("SELECT first_name, last_name FROM user WHERE id = %s", (university_id,))
    student = cursor.fetchone()
    myDb.commit()
    cursor.close()
    
    return render_template("fillReviewForm.html", university_id = university_id, advisors = advisors, appForm = appForm, student = student)

@apps.route("/submitFinalDecision", methods=['GET','POST'])
@login_required
@authorize(["faculty", "sysadmin", "gs"])
def submitFinalDecision():
    cursor = myDb.cursor(dictionary = True)

    university_id = int(request.form["studentID"])
    advisor = request.form["advisorId"] if 'advisorId' in request.form else None
    decision = request.form["decision"] if 'decision' in request.form else None
    cursor.execute("UPDATE applicant SET appStatus = %s WHERE university_id = %s", (decision, university_id))
    cursor.execute("UPDATE applicationForm SET recommended_advisor = %s WHERE university_id = %s", (advisor, university_id))

    myDb.commit()
    cursor.close()
    return redirect(url_for('.applicants'))


@apps.route('/submitReviewForm', methods=['GET','POST'])
@login_required
@authorize(["faculty", "sysadmin"])
def submitReviewForm():
    cursor = myDb.cursor(dictionary = True)

    university_id = int(request.form["studentID"])
    reviewer = session['userId']
    r1rating = request.form["r1rating"] if 'r1rating' in request.form else None
    r1generic = request.form["r1generic"] if 'r1generic' in request.form else None
    r1credible = request.form["r1credible"] if 'r1credible' in request.form else None
    r1from = request.form["r1from"] if 'r1from' in request.form else None
    r2rating = request.form["r2rating"] if 'r2rating' in request.form else None
    r2generic = request.form["r2generic"] if 'r2generic' in request.form else None
    r2credible = request.form["r2credible"] if 'r2credible' in request.form else None
    r2from = request.form["r2from"] if 'r2from' in request.form else None
    r3rating = request.form["r3rating"] if 'r3rating' in request.form else None
    r3generic = request.form["r3generic"] if 'r3generic' in request.form else None
    r3credible = request.form["r3credible"] if 'r3credible' in request.form else None
    r3from = request.form["r3from"] if 'r3from' in request.form else None
    GASrating = request.form["GASrating"] if 'GASrating' in request.form else None
    deficiencies = request.form["deficiencies"] if 'deficiencies' in request.form else None
    rejectReason = request.form["rejectReason"] if 'rejectReason' in request.form else None
    thoughts = request.form["thoughts"] if 'thoughts' in request.form else None
    semesterApplied = request.form["semesterApplied"] if 'semesterApplied' in request.form else None

    # check if application is complete
    appIncomplete(university_id)
    cursor.execute("SELECT appStatus FROM applicant WHERE university_id = %s", (university_id,))
    appStatus = cursor.fetchone()    
    if appStatus['appStatus'] not in ["Complete", "Under Review"]:
        flash("The application is not complete. You cannot submit a review form until it's complete.", "danger")
        myDb.commit()
        cursor.close()
        return redirect(url_for('.applicants'))
    
    # check if review form has already been submitted by this user
    cursor.execute("SELECT * FROM reviewForm WHERE university_id = %s AND reviewer = %s", (university_id, session['userId']))
    if cursor.fetchone():
        flash("You have already submitted a review form for this applicant.", "danger")
        myDb.commit()
        cursor.close()
        return redirect(url_for('.applicants'))

    cursor.execute("INSERT INTO reviewForm (university_id,reviewer,r1rating,r1generic,r1credible,r1from,r2rating,r2generic,r2credible,r2from,r3rating,r3generic,r3credible,r3from,GASrating,deficiencies,rejectReason,thoughts,semesterApplied) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)", (university_id,reviewer,r1rating,r1generic,r1credible,r1from,r2rating,r2generic,r2credible,r2from,r3rating,r3generic,r3credible,r3from,GASrating,deficiencies,rejectReason,thoughts,semesterApplied))
    myDb.commit()

    cursor.execute("UPDATE applicant SET appStatus = %s WHERE university_id = %s", ("Under Review",university_id))
    myDb.commit()

    cursor.close()
    return redirect(url_for('.applicants'))

@apps.route("/applicationFillout")
@login_required
@authorize(["applicant"])
def applicationFillout():
    cursor = myDb.cursor(dictionary = True)
    cursor.execute("SELECT first_name, last_name FROM user WHERE id = %s", (session["userId"],))
    student = cursor.fetchone()
    
    myDb.commit()
    cursor.close()
    return render_template("applicationFillout.html", student=student)
    
@apps.route("/applicationEdit/<int:university_id>")
@login_required
@authorize(["applicant", "sysadmin", "gs", "faculty"])
def applicationEdit(university_id):
    # if applicant, check if they are editing their own application
    if session["userType"] == 'applicant' and session["userId"] != university_id:
        flash("You are not authorized to edit this application.", "danger")
        return redirect(url_for('index'))

    cursor = myDb.cursor(dictionary = True)

    # faculty info
    cursor.execute("SELECT * FROM faculty_info WHERE user_id = %s", (session['userId'],))
    faculty_info = cursor.fetchone()

    # check if application is complete
    appIncomplete(university_id)
    cursor.execute("SELECT appStatus FROM applicant WHERE university_id = %s", (university_id,))
    appStatus = cursor.fetchone()
    if session['userType'] == 'applicant' and appStatus['appStatus'] not in ["Incomplete", "Complete"]:
        flash("The application is not editable.", "danger")
        myDb.commit()
        cursor.close()
        return redirect(url_for('index'))
    
    # get application info
    cursor.execute("SELECT * FROM applicant WHERE university_id = %s", (university_id,))
    application = cursor.fetchone()
    if application is None:
        flash("The application does not exist.", "danger")
        myDb.commit()
        cursor.close()
        return redirect(url_for('index'))
    
    cursor.execute("SELECT * FROM applicationForm WHERE university_id = %s", (university_id,))
    application['form'] = cursor.fetchone()
    if application['form'] is None:
        flash("The application does not exist.", "danger")
        myDb.commit()
        cursor.close()
        return redirect(url_for('index'))
    
    # if faculty, must be the chair
    if session["userType"] == 'faculty':
        if faculty_info['is_admissions_chair'] != 1:
            flash("You are not authorized to edit this application.", "danger")
            myDb.commit()
            cursor.close()
            return redirect(url_for('.applicants'))

    cursor.execute("SELECT id, first_name, last_name FROM user WHERE id = %s", (university_id,))
    student = cursor.fetchone()
    
    myDb.commit()
    cursor.close()
    return render_template("applicationEdit.html", student=student, application=application, appStatus = appStatus, faculty_info = faculty_info)

@apps.route ("/postSubmittingApp", methods=['GET', 'POST'])
@login_required
@authorize(["applicant"])
def postSubmittingApp():
    if request.method == 'POST':
        
        university_id = session['userId']
        
        degreeSeeking = request.form["degreeSeeking"]
        if "MScheck" not in request.form:
            MScheck = 0
        else:
            MScheck = request.form["MScheck"]
        MSmajor = request.form["MSmajor"]
        MSuniversity = request.form["MSuniversity"]
        if(request.form["MSgpa"] == ""):
            MSgpa = ""
        else:
            MSgpa = float(request.form["MSgpa"])

        if(request.form["MSyear"] == ""):
            MSyear = 0
        else:
            MSyear = int(request.form["MSyear"])
        BAcheck = request.form["BAcheck"]
        BAmajor = request.form["BAmajor"]
        if(request.form["BAyear"] == ""):
            BAyear = 0
        else:
            BAyear = int(request.form["BAyear"])
        BAuniversity = request.form["BAuniversity"]
        if(request.form["BAgpa"] == ""):
            BAgpa = ""
        else:
            BAgpa = float(request.form["BAgpa"])
        if(request.form["GREverbal"] == ""):
            GREverbal = 0
        else:
            GREverbal = int(request.form["GREverbal"])
        if(request.form["GREquantitative"] == ""):
            GREquantitative = 0
        else:
            GREquantitative = int(request.form["GREquantitative"])
        if(request.form["GREyear"] == ""):
            GREyear = 0
        else:
            GREyear = int(request.form["GREyear"])
        if(request.form["GREadvancedScore"] == ""):
            GREadvancedScore = 0
        else:
            GREadvancedScore = int(request.form["GREadvancedScore"])
        GREadvancedSubject = request.form["GREadvancedSubject"]
        if(request.form["TOEFLscore"] == ""):
            TOEFLscore = 0
        else:
            TOEFLscore = int(request.form["TOEFLscore"])
        TOEFLdate = request.form["TOEFLdate"]
        priorWork = request.form["priorWork"]
        startDate = request.form["startDate"]
        # cursor = myDb.cursor(dictionary= True)
        # #check to see if they have applied before 
        # cursor.execute("SELECT startDate FROM applicationForm WHERE university_id = %s", (request.form["university_id"]))
        # sd = cursor.fetchone()
        # if startDate == sd:
        #     return redirect(url_for('.applicationFillout'))
        transcriptStatus = "Not Received"
        r1status = "Not Received"
        r1writer = request.form["r1writer"]
        r1email = request.form["r1email"]
        r1title = request.form["r1title"]
        r1affiliation = request.form["r1affiliation"]
        r1letter = ""
        r2status = "Not Received"
        r2writer = request.form["r2writer"]
        r2email = request.form["r2email"]
        r2title = request.form["r2title"]
        r2affiliation = request.form["r2affiliation"]
        r2letter =  ""
        r3status = "Not Received"
        r3writer =  request.form["r3writer"]
        r3email = request.form["r3email"]
        r3title = request.form["r3title"]
        r3affiliation = request.form["r3affiliation"]
        r3letter =   ""
        cursor = myDb.cursor(dictionary= True)
        cursor.execute (
            "INSERT INTO applicationForm (university_id, degreeSeeking,MScheck,MSmajor,MSyear,MSuniversity,MSgpa,BAcheck,BAmajor,BAyear,BAuniversity,BAgpa,GREverbal,GREquantitative,GREyear,GREadvancedScore,GREadvancedSubject,TOEFLscore,TOEFLdate,priorWork,startDate,transcriptStatus,r1status,r1writer,r1email,r1title,r1affiliation,r1letter,r2status,r2writer,r2email,r2title,r2affiliation,r2letter,r3status,r3writer,r3email,r3title,r3affiliation,r3letter) VALUES (%s, %s, %s, %s,%s, %s, %s, %s,%s, %s, %s, %s,%s, %s, %s, %s,%s, %s, %s, %s, %s,%s, %s, %s, %s,%s, %s, %s,%s, %s, %s, %s,%s, %s, %s, %s,%s, %s, %s, %s)", (university_id, degreeSeeking,MScheck,MSmajor,MSyear,MSuniversity,MSgpa,BAcheck,BAmajor,BAyear,BAuniversity,BAgpa,GREverbal,GREquantitative,GREyear,GREadvancedScore,GREadvancedSubject,TOEFLscore,TOEFLdate,priorWork,startDate,transcriptStatus,r1status,r1writer,r1email,r1title,r1affiliation,r1letter,r2status,r2writer,r2email,r2title,r2affiliation,r2letter,r3status,r3writer,r3email,r3title,r3affiliation,r3letter)
        )
        myDb.commit()

        appStatus = "Incomplete"
        cursor.execute("UPDATE applicant SET appStatus = %s WHERE university_id = %s", (appStatus,university_id))
        myDb.commit()
        cursor.close()

        return redirect(url_for('index'))

    return redirect(url_for('.applicationFillout'))

@apps.route ("/postSubmittingAppEdit", methods=['GET', 'POST'])
@login_required
@authorize(["applicant", "sysadmin", "gs", "faculty"])
def postSubmittingAppEdit():
    if request.method == 'POST':
        
        university_id = request.form["university_id"]
        degreeSeeking = request.form["degreeSeeking"]
        if "MScheck" not in request.form:
            MScheck = 0
        else:
            MScheck = request.form["MScheck"]
        MSmajor = request.form["MSmajor"]
        MSuniversity = request.form["MSuniversity"]
        if(request.form["MSgpa"] == ""):
            MSgpa = 0
        else:
            MSgpa = float(request.form["MSgpa"])

        if(request.form["MSyear"] == ""):
            MSyear = 0
        else:
            MSyear = int(request.form["MSyear"])
        BAcheck = request.form["BAcheck"]
        BAmajor = request.form["BAmajor"]
        if(request.form["BAyear"] == ""):
            BAyear = 0
        else:
            BAyear = int(request.form["BAyear"])
        BAuniversity = request.form["BAuniversity"]
        if(request.form["BAgpa"] == ""):
            BAgpa = 0
        else:
            BAgpa = float(request.form["BAgpa"])
        if(request.form["GREverbal"] == ""):
            GREverbal = 0
        else:
            GREverbal = int(request.form["GREverbal"])
        if(request.form["GREquantitative"] == ""):
            GREquantitative = 0
        else:
            GREquantitative = int(request.form["GREquantitative"])
        if(request.form["GREyear"] == ""):
            GREyear = 0
        else:
            GREyear = int(request.form["GREyear"])
        if(request.form["GREadvancedScore"] == ""):
            GREadvancedScore = 0
        else:
            GREadvancedScore = int(request.form["GREadvancedScore"])
        GREadvancedSubject = request.form["GREadvancedSubject"]
        if(request.form["TOEFLscore"] == ""):
            TOEFLscore = 0
        else:
            TOEFLscore = int(request.form["TOEFLscore"])
        TOEFLdate = request.form["TOEFLdate"]
        priorWork = request.form["priorWork"]
        startDate = request.form["startDate"]
        r1writer = request.form["r1writer"]
        r1email = request.form["r1email"]
        r1title = request.form["r1title"]
        r1affiliation = request.form["r1affiliation"]
        r2writer = request.form["r2writer"]
        r2email = request.form["r2email"]
        r2title = request.form["r2title"]
        r2affiliation = request.form["r2affiliation"]
        r3writer =  request.form["r3writer"]
        r3email = request.form["r3email"]
        r3title = request.form["r3title"]
        r3affiliation = request.form["r3affiliation"]
        cursor = myDb.cursor(dictionary= True)
        cursor.execute (
            "UPDATE applicationForm SET degreeSeeking=%s, MScheck=%s, MSmajor=%s, MSyear=%s, MSuniversity=%s, MSgpa=%s, BAcheck=%s, BAmajor=%s, BAyear=%s, BAuniversity=%s, BAgpa=%s, GREverbal=%s, GREquantitative=%s, GREyear=%s, GREadvancedScore=%s, GREadvancedSubject=%s, TOEFLscore=%s, TOEFLdate=%s, priorWork=%s, startDate=%s, r1writer=%s, r1email=%s, r1title=%s, r1affiliation=%s, r2writer=%s, r2email=%s, r2title=%s, r2affiliation=%s, r3writer=%s, r3email=%s, r3title=%s, r3affiliation=%s WHERE university_id=%s", (degreeSeeking,MScheck,MSmajor,MSyear,MSuniversity,MSgpa,BAcheck,BAmajor,BAyear,BAuniversity,BAgpa,GREverbal,GREquantitative,GREyear,GREadvancedScore,GREadvancedSubject,TOEFLscore,TOEFLdate,priorWork,startDate,r1writer,r1email,r1title,r1affiliation,r2writer,r2email,r2title,r2affiliation,r3writer,r3email,r3title,r3affiliation, university_id)
        )
        myDb.commit()

        cursor.close()
        return redirect(url_for('index'))
    
    return redirect(url_for('.applicationEdit'))

@apps.route('/accept')
@login_required
@authorize(['applicant'])
def acceptApp():
    cursor = myDb.cursor(dictionary=True)

    # ensure that the applicant has been admitted
    cursor.execute("SELECT appStatus FROM applicant WHERE university_id = %s AND appStatus LIKE 'Admit%'", (session['userId'],))
    appStatus = cursor.fetchone()
    if appStatus is None:
        flash("You have not been admitted. You cannot accept an admissions offer.")
        myDb.commit()
        cursor.close()
        return redirect(url_for('index'))

    # ensure that the applicant has not already accepted an offer
    cursor.execute("SELECT appStatus FROM applicant WHERE university_id = %s AND appStatus = 'Accepted'", (session['userId'],))
    appStatus = cursor.fetchone()
    if appStatus is not None:
        flash("You have already accepted an admissions offer.")
        myDb.commit()
        cursor.close()
        return redirect(url_for('index'))
    
    # update the applicant's status to accepted
    cursor.execute("UPDATE applicant SET appStatus = 'Accepted' WHERE university_id = %s", (session['userId'],))
    myDb.commit()

    cursor.close()
    return redirect(url_for('index'))

@apps.route('/matriculate', methods=['POST'])
@login_required
@authorize(['gs', 'sysadmin'])
def matriculate():
    university_id = int(request.form['studentId'])
    advisor_id = int(request.form['advisorId'])
    grad_semester = request.form['gradSemester']
    grad_year = int(request.form['gradYear'])

    cursor = myDb.cursor(dictionary=True)

    # ensure that the applicant has accepted their offer
    cursor.execute("SELECT appStatus FROM applicant WHERE university_id = %s AND appStatus = 'Accepted'", (university_id,))
    appStatus = cursor.fetchone()
    if appStatus is None:
        flash("The applicant has not accepted their offer of admission. You cannot matriculate them.")
        myDb.commit()
        cursor.close()
        return redirect(url_for('.applicants'))
    
    # update the applicant's status to matriculated
    cursor.execute("UPDATE applicant SET appStatus = 'Matriculated' WHERE university_id = %s", (university_id,))

    # get the applicant's program
    cursor.execute("SELECT degreeSeeking FROM applicationForm WHERE university_id = %s", (university_id,))
    degreeSeeking = cursor.fetchone()['degreeSeeking']

    # insert the applicant into the student table
    cursor.execute("INSERT INTO student_info (user_id, program, advisor_id, grad_semester, grad_year) VALUES (%s, %s, %s, %s, %s)", (university_id, degreeSeeking, advisor_id, grad_semester, grad_year))

    # update the user's type
    cursor.execute("UPDATE user SET type = 'student' WHERE id = %s", (university_id,))

    myDb.commit()
    cursor.close()

    flash("The applicant has been matriculated.", "success")

    return redirect(url_for('.applicants'))

@apps.route('/rec-letter/<int:university_id>', methods=["GET", "POST"])
def rec_letter(university_id):
    cursor = myDb.cursor(dictionary=True)

    if request.method == 'POST':
        email = request.form['email']
        letter = request.form['letter']

        # check if submitter is a recommender
        cursor.execute("SELECT `r1email`, `r1letter`, `r2email`, `r2letter`, `r3email`, `r3letter` FROM `applicationForm` WHERE `university_id` = %s", (university_id,))
        recommenders = cursor.fetchone()
        if recommenders == None:
            flash('Requested applicant does not exist.', 'danger')
            myDb.commit()
            cursor.close()
            return redirect(url_for('index'))

        # determine which recommender this is, if valid
        recommender = 0
        if email == recommenders['r1email'] and recommenders['r1letter'] in ["", None]:
            recommender = 1
        elif email == recommenders['r2email'] and recommenders['r2letter'] in ["", None]:
            recommender = 2
        elif email == recommenders['r3email'] and recommenders['r3letter'] in ["", None]:
            recommender = 3
        else:
            flash('You are not a recommender for this applicant and/or you have already submitted a recommendation for this applicant.', 'warning')
            myDb.commit()
            cursor.close()
            return redirect(url_for('index'))
        
        # insert recommenders letter
        cursor.execute("UPDATE `applicationForm` SET `r"+str(recommender)+"letter` = %s, `r"+str(recommender)+"status` = %s WHERE `university_id` = %s", (letter, "Received", university_id))

        myDb.commit()

        # check if application is complete now that letter received
        appIncomplete(university_id)

        cursor.close()
        flash("Thank you for submitting your recommendation letter!", "success")
        return redirect(url_for('.rec_letter', university_id=university_id))

    # ensure that user has an application
    cursor.execute("SELECT `university_id`, `r1letter`, `r2letter`, `r3letter` FROM `applicationForm` WHERE `university_id` = %s", (university_id,))
    app = cursor.fetchone()
    if app == None:
        flash('Requested applicant does not exist.', 'danger')
        myDb.commit()
        cursor.close()
        return redirect(url_for('index'))
    if app['r1letter'] != '' and app['r1letter'] != None and app['r2letter'] != '' and app['r2letter'] != None and app['r3letter'] != '' and app['r3letter'] != None:
        flash('Applicant does not have any pending recommendation letters.', 'info')
        myDb.commit()
        cursor.close()
        return redirect(url_for('index'))

    # get applicant name
    cursor.execute("SELECT `id`, `first_name`, `last_name` FROM `user` WHERE `id` = %s", (university_id,))
    student = cursor.fetchone()

    myDb.commit()
    cursor.close()
    return render_template('rec_letter.html', student = student)

@apps.route('/uploadTranscript', methods=['POST'])
# @login_required
# @authorize(['applicant'])
def uploadTranscript():
    cursor = myDb.cursor(dictionary=True)
    #cursor.execute("SELECT startDate FROM applicationFillout WHERE university_id = %s" (session['university_id']))
    file = request.files['file']
    file_name = file.filename
    mimetype = file.mimetype
    file_data = file.read()
    cursor.execute("INSERT INTO transcript (trans_id, file_name, mimetype, file_data) VALUES (%s, %s, %s, %s)", (session['id'],file_name, mimetype, file_data))
    myDb.commit()
    cursor.close()
    return redirect(url_for("index", trans_id=session['id']))
    
    

@apps.route('/downloadTranscript/<int:trans_id>')
# @login_required
# @authorize(['applicant'])
def downloadTranscript(trans_id):
    cursor = myDb.cursor(dictionary=True)
    
    cursor.execute("SELECT file_data FROM transcript WHERE trans_id=%s", (trans_id,))
    file_data = cursor.fetchone()
    file_data = file_data['file_data']
    # send the PDF file as a response
    myDb.commit()
    cursor.close()
    return send_file(BytesIO(file_data), download_name='document.pdf', as_attachment=True)

@apps.route('/mail_transcript')
def mail_transcript():
    mail_transcript = "Yes"
    print ("works")
    cursor = myDb.cursor(dictionary=True)
    cursor.execute("UPDATE applicant SET mail_transcript = %s WHERE university_id = %s", (mail_transcript, session['id'],))
    myDb.commit()
    # change db
    cursor.close()
    return redirect(url_for("index"))
   
    