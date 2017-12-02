from datetime import datetime
from flask import Flask, request, render_template, redirect
import MySQLdb

application = Flask(__name__)

url = 'http://localhost:8080'

# Connect to database.
def connect_db():
    
    db = MySQLdb.connect( user='root', passwd='YutaOkinawa1211', host='localhost', db='tukutter', charset='utf8')
    return db

# Run this process before every route() function.
@application.before_request
def pre_request():

    # Consider signed in if 'True' at session.
    if session.get('signin'):
        return
    
    # No check if sign in page is requested.
    elif request.path == '/signin':
        return

    #
    else:
        return redirect( url + '/static/signin.html' ) 
    
# Redirect access from root to login.
@application.route('/')
def root_access():

    global url

    # Redirect to login page.
    return redirect( url + '/static/signin.html' )

# Add new user.
@application.route('/signup', methods=['POST'])
def signup():

    global url
    
    # Check password.
    if request.form['password'] != request.form['conf_password']:
        return render_template( 'error.html', message='パスワードが一致していません。' )

    # Connect to database.
    db = connect_db()
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

# Process signin.
@application.route('/signin', methods=['POST'])
def signin():

    

# Show top menu.
@application.route('/top', methods=['POST'])
def top():

    global url
    
    # Find login user.

    # Get login user's value from web form.
    login_id = request.form['login_id']
    in_pass = request.form['password']
    
    # Connect to database.
    db = connect_db()
    connect = db.cursor()

    # Find the user's id, username, and password.
    sql = 'select id, username, password from user where active_flg = 1 and login_id = %s'
    connect.execute( sql, [login_id] )
    result = connect.fetchall()

    # [Not equiped] If login_id is not found, show error page.
    
    user_id   = result[0][0]
    username  = result[0][1]
    corr_pass = result[0][2]

    # Reject incorrect password.
    if in_pass != corr_pass:
        return render_template( 'error.html', message='パスワードが間違っています。' )

    # Get users who are followed by login user.
    sql = 'select user_id from follow where active_flg = 1 and follower_id = %s'
    connect.execute( sql, [user_id] )
    result = connect.fetchall()

    # flw_id = [0] * len(result)
    
    for num in range(len(result)):
        # flw_id[num] = result[num][0]
        flw_id.append(result[num][0])
                      
    flw_id.append(user_id)
        
    # Get tweets.
    sql = 'select id, user_id, content, time from tweet where active_flg = 1 and user_id = %s'
    
    for num in range(len(flw_id)-1):
        sql = sql + ' or user_id = %s'

    sql = sql + ' order by time desc'
    
    connect.execute( sql, flw_id )
    result = connect.fetchall()
        
    return result[0][3].strftime('%Y/%m/%d %H:%M')
    
    
