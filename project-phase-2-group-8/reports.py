from flask import render_template, request, redirect, url_for, Blueprint, session
from helpers import authorize, myDb, login_required
from students import programTypes

reports = Blueprint('reports', __name__, template_folder='templates/reports')

@reports.route("/")
@login_required
@authorize(["faculty", "gs", "sysadmin"])
def index():
    cursor = myDb.cursor(dictionary=True)

    facultyType = {
        "advisor": False,
        "instructor": False,
        "reviewer": False,
        "admissions_chair": False
    }
    advisors = None
    if session['userType'] == 'faculty':
        # get faculty type
        cursor.execute("SELECT `is_advisor`, `is_reviewer`, `is_instructor`, `is_admissions_chair` FROM `faculty_info` WHERE `user_id` = %s", (session['userId'],))
        faculty_info = cursor.fetchone()
        facultyType['advisor'] = faculty_info['is_advisor']
        facultyType['instructor'] = faculty_info['is_instructor']
        facultyType['reviewer'] = faculty_info['is_reviewer']
        facultyType['admissions_chair'] = faculty_info['is_admissions_chair']
    else:
        # get advisors
        cursor.execute("SELECT `user_id`, `first_name`, `last_name` FROM `faculty_info` INNER JOIN `user` ON `user`.`id` = `faculty_info`.`user_id` WHERE `is_advisor` = 1")
        advisors = cursor.fetchall()
    myDb.commit()
    cursor.close()

    return render_template("index.html",
                           facultyType = facultyType,
                           advisors = advisors)

@reports.route("/graduating")
@login_required
@authorize(["gs", "sysadmin"])
def graduating_students():

    semester = request.args.get('semester')
    year = request.args.get('year')
    degree = request.args.get('degree')

    params = []

    query = "SELECT `user_id`, `first_name`, `last_name`, `grad_semester`, `grad_year`, `program` FROM `student_info` INNER JOIN `user` on `user`.`id` = `student_info`.`user_id` WHERE `grad_status` = 'cleared'"
    if semester != None and semester != "":
        query += " AND `grad_semester` = %s"
        params.append(semester)
    if year != None and year != "":
        query += " AND `grad_year` = %s"
        params.append(year)
    if degree != None and degree != "":
        query += " AND `program` = %s"
        params.append(degree)

    cursor = myDb.cursor(dictionary=True)
    cursor.execute(query, tuple(params))
    students = cursor.fetchall()

    cursor.execute("SELECT DISTINCT `grad_year` AS `year` FROM `student_info` WHERE `grad_status` = 'cleared' ORDER BY `year` DESC")
    years = cursor.fetchall()

    myDb.commit()
    cursor.close()
    return render_template("graduating_students.html", students=students, years=years, programTypes = programTypes)

@reports.route("/alumni")
@login_required
@authorize(["gs", "sysadmin"])
def alumni():

    semester = request.args.get('semester')
    year = request.args.get('year')
    degree = request.args.get('degree')

    params = []

    query = "SELECT `user_id`, `first_name`, `last_name`, `email`, `grad_semester`, `grad_year`, `program` FROM `alumni_info` INNER JOIN `user` on `user`.`id` = `alumni_info`.`user_id`"
    if semester != None and semester != "":
        query += " AND `grad_semester` = %s"
        params.append(semester)
    if year != None and year != "":
        query += " AND `grad_year` = %s"
        params.append(year)
    if degree != None and degree != "":
        query += " AND `program` = %s"
        params.append(degree)

    cursor = myDb.cursor(dictionary=True)
    cursor.execute(query, tuple(params))
    students = cursor.fetchall()

    cursor.execute("SELECT DISTINCT `grad_year` AS `year` FROM `alumni_info` ORDER BY `year` DESC")
    years = cursor.fetchall()

    myDb.commit()
    cursor.close()
    return render_template("alumni.html", students=students, years=years, programTypes = programTypes)

@reports.route("/transcript", methods=['POST'])
@login_required
def transcript():
    student = request.form['studentId']
    student = int(student) # removes leading zeros

    return redirect(url_for('ads.transcript.view', userId=student))

@reports.route("/applicant-stats")
@login_required
@authorize(["gs", "sysadmin"])
def applicantStats():
    cursor = myDb.cursor(dictionary=True)

    semester = request.args.get('semester')
    degree = request.args.get('degree')

    # get total applicants
    params = []
    query = "SELECT COUNT(*) AS `total` FROM `applicationForm` WHERE 1"
    if semester != None and semester != "":
        query += " AND `startDate` = %s"
        params.append(semester)
    if degree != None and degree != "":
        query += " AND `degreeSeeking` = %s"
        params.append(degree)

    cursor.execute(query, tuple(params))
    total = cursor.fetchone()['total']

    # get applicants by status
    params = []
    query = "SELECT `appStatus`, COUNT(*) AS `count` FROM `applicant` INNER JOIN `applicationForm` ON `applicant`.`university_id` = `applicationForm`.`university_id` WHERE 1"
    if semester != None and semester != "":
        query += " AND `startDate` = %s"
        params.append(semester)
    if degree != None and degree != "":
        query += " AND `degreeSeeking` = %s"
        params.append(degree)
    query += " GROUP BY `appStatus`"

    cursor.execute(query, tuple(params))
    statuses = cursor.fetchall()
    # combine all other statuses into other, set colors
    other = 0
    for s in statuses:
        if s['appStatus'] not in ['Under Review', 'Admit', 'Admit With Aid', 'Reject', 'Accepted']:
            other += s['count']
        if s['appStatus'] == 'Admit':
            s['color'] = '#2ecc71'
        elif s['appStatus'] == 'Admit With Aid':
            s['color'] = '#27ae60'
        elif s['appStatus'] == 'Accepted':
            s['color'] = '#27ae60'
        elif s['appStatus'] == 'Reject':
            s['color'] = '#e74c3c'
        elif s['appStatus'] == 'Under Review':
            s['color'] = '#95a5a6'
    if other > 0:
        statuses.append({'appStatus': 'Other', 'count': other, 'color': '#95a5a6'})
    
    # get applications by submission date
    params = []
    query = "SELECT `date_submitted`, COUNT(*) AS `count` FROM `applicationForm` WHERE 1"
    if semester != None and semester != "":
        query += " AND `startDate` = %s"
        params.append(semester)
    if degree != None and degree != "":
        query += " AND `degreeSeeking` = %s"
        params.append(degree)
    query += " GROUP BY DATE(`date_submitted`) ORDER BY `date_submitted` ASC"

    cursor.execute(query, tuple(params))
    submissions = cursor.fetchall()

    # get average test scores
    params = []
    query = "SELECT AVG(`GREverbal`) AS `GREverbal`, AVG(`GREquantitative`) AS `GREquantitative`, AVG(`GREadvancedScore`) AS `GREadvancedScore`, AVG(`TOEFLscore`) AS `TOEFLscore` FROM `applicationForm` INNER JOIN `applicant` ON `applicant`.`university_id` = `applicationForm`.`university_id` WHERE appStatus IN ('Admit', 'Admit With Aid')"
    if semester != None and semester != "":
        query += " AND `startDate` = %s"
        params.append(semester)
    if degree != None and degree != "":
        query += " AND `degreeSeeking` = %s"
        params.append(degree)

    cursor.execute(query, tuple(params))
    scores = cursor.fetchone()

    # get average GPA
    params = []
    query = "SELECT AVG(`MSgpa`) AS `MSgpa`, AVG(`BAgpa`) AS `BAgpa` FROM `applicationForm` INNER JOIN `applicant` ON `applicant`.`university_id` = `applicationForm`.`university_id` WHERE appStatus IN ('Admit', 'Admit With Aid', 'Accepted', 'Matriculated')"
    if semester != None and semester != "":
        query += " AND `startDate` = %s"
        params.append(semester)
    if degree != None and degree != "":
        query += " AND `degreeSeeking` = %s"
        params.append(degree)

    cursor.execute(query, tuple(params))
    gpas = cursor.fetchone()
    
    myDb.commit()
    cursor.close()
    return render_template("applicant-stats.html",
                           total = total,
                           statuses = statuses,
                           submissions = submissions,
                           scores = scores,
                           gpas = gpas,)
