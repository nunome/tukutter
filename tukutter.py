from flask import Flask, request, render_template, redirect
import MySQLdb

application = Flask(__name__)

# url = 'http://localhost:8080'

# Redirect access from root to login.
@application.route('/')
def index():

    url = 'http://localhost:8080'
    
    # Redirect to login page.
    return redirect( url + '/static/login.html' )

# Add new user.
@application.route('/signup', methods=['POST'])
def signup():

    url = 'http://localhost:8080'
    
    # Check password.
    if request.form['password'] != request.form['conf_password']:
        return 'パスワードが一致していません。'

    # Connect to database.
    db = MySQLdb.connect( user='root', passwd='YutaOkinawa1211', host='localhost', db='tukutter', charset='utf8')
    connect = db.cursor()

    # Add new user to "user" table.
    sql = 'insert into user( login_id, password, username ) value ( %s, %s, %s )'
    connect.execute( sql, [ request.form['login_id'], request.form['password'], request.form['username'] ] )
    db.commit()

    # Disconnect form database.
    db.close()
    connect.close()

    # Jump to login menu.
    # [Need to change] Jump to top menu. 
    return redirect( url + '/static/login.html' )

# Show top menu.
@application.route('/top', methods=['POST'])
def top():

    url = 'http://localhost:8080'
    
    # Find login user.

    # Get login user's value from web form.
    login_id = request.form['login_id']
    in_pass = request.form['password']
    
    # Connect to database.
    db = MySQLdb.connect( user='root', passwd='YutaOkinawa1211', host='localhost', db='tukutter', charset='utf8')
    connect = db.cursor()

    # Find the user's id, username, password.
    sql = 'select id, username, password from user where login_id = %s'
    connect.execute( sql, [login_id] )
    result = connect.fetchall()

    user_id   = result[0][0]
    username  = result[0][1]
    corr_pass = result[0][2]

    # Reject incorrect password.
    if in_pass != corr_pass:
        return 'パスワードが間違っています。'

    # Get users who are followed by login user.
    sql = 'select user_id from follow where follower_id = %s'
    connect.execute( sql, [user_id] )
    result = connect.fetchall()

    flw_id = [0] * len(result)
    
    for num in range(len(result)):
        flw_id[num] = result[num][0]

    flw_id = flw_id.append(user_id)
    
    # Get tweets.
    sql = 'select id, user_id, content, time from tweet where user_id = %s'
    connect.execute( sql, [flw_id] )
    result = []
    result = connect.fetchall()

    print(result[0][0])
    
    return 'aaa' 
    
    
