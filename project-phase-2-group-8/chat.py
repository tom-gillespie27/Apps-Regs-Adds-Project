from flask import render_template, request, redirect, url_for, Blueprint, session
from helpers import authorize, myDb, login_required

chat = Blueprint('chat', __name__, template_folder='templates')

@chat.route("/")
@login_required
@authorize(["alum"])
def index():    
    # Create a cursor to execute queries
    cursor = myDb.cursor(dictionary=True)

    # Get messages
    cursor.execute("SELECT `alumni_chat_messages`.*, `user`.`first_name`, `user`.`last_name` FROM `alumni_chat_messages` INNER JOIN `user` ON `user`.`id` = `alumni_chat_messages`.`user_id` ORDER BY `timestamp` DESC")
    messages = cursor.fetchall()
    
    myDb.commit()
    cursor.close()
    return render_template("chat.html", messages=messages)

@chat.route("/send", methods=["POST"])
@login_required
@authorize(["alum"])
def send():
    # Create a cursor to execute queries
    cursor = myDb.cursor(dictionary=True)

    # Get message
    message = request.form['message']

    # Insert message
    cursor.execute("INSERT INTO `alumni_chat_messages` (`message`, `user_id`) VALUES (%s, %s)", (message, session["userId"]))
    myDb.commit()
    cursor.close()
    return redirect(url_for(".index"))