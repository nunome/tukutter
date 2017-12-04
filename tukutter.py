from datetime import datetime
import os
from flask import Flask, request, render_template, redirect, session, url_for
import MySQLdb

application = Flask(__name__)

application.secret_key = os.urandom(24)

url = 'http://localhost:8080'

# Connect to database.
def connect_db():
    
    db = MySQLdb.connect( user='root', passwd='YutaOkinawa1211', host='localhost', db='tukutter', charset='utf8')
    return db

# Publish session ID.
def publish_session( user_ID, username, signin ):

    session['user_id']  = user_id
    session['username'] = username
    session['signin']   = True

# Publish cookie.
def publish_cookie( resp, login_id, password ):

    global url
    
    max_age = 60*60*24 # 1day
    expires = int( datetime.now().timestamp() ) + max_age
    
    resp.set_cookie( 'login_id', login_id, 'password', password,
                     max_age=max_age, expires=expires, domain=url )

# Run this process before every route() function.
@application.before_request
def pre_request():

    global url
    
    # Consider signed in if 'True' at session.
    if session.get('signin'):
        return
    
    # No check if sign in page is requested.
    if request.path == '/signin':
        return

    cookie_lid = request.cookies.get( 'login_id', None )
    
    if cookie_lid == None:
        # Redirect to sign in page.
        return redirect( url + '/static/signin.html' )
    
    else:
        # Collate password
        cookie_pw = request.cookies.get( 'password' )

        # Connect to database.
        db = connect_db()
        connect = db.cursor()

        # Find the user's id, username, and password.
        sql = 'select id, username, password from user where active_flg = 1 and login_id = %s'
        connect.execute( sql, [cookie_lid] )
        result = connect.fetchall()
    
        user_id   = result[0][0]
        username  = result[0][1]
        password  = result[0][2]
        
        if cookie_pw == password:
            # Publish session ID.
            publish_session( user_id, username, True )
            
            # Redirect to requested page.
            return

        else:
            # Redirect to sign in page.
            return redirect( url + '/static/signin.html' )

# Redirect access from root to sign in page.
@application.route('/')
def root_access():

    # Redirect to login page.
    return redirect( url_for('top') )

# Add new user.
@application.route('/signup', methods=['POST'])
def signup():

    global url

    login_id      =      request.form['login_id']
    password      =      request.form['password']
    conf_password = request.form['conf_password']
    username      =      request.form['username']
    
    # Collate password.
    if password != conf_password:
        return render_template( 'error.html', message='パスワードが一致していません。' )

    # Connect to database.
    db = connect_db()
    connect = db.cursor()
    
    # Add new user to "user" table.
    sql = 'insert into user( login_id, password, username ) value ( %s, %s, %s )'
    connect.execute( sql, [ login_id, password, username ] )
    db.commit()

    # Get user_ID from SQL server.
    sql = 'select id from user where active_flg = 1 and login_id = %s'
    connect.execute( sql, login_id )
    user_id = connect.fetchall() # [0][0]
    
    # Publish session ID.
    publish_session( user_id, username, True )

    # Publish cookie.
    publish_cookie( redirect( url_for('top' ) ), login_id, password )
    
    # Disconnect form database.
    db.close()
    connect.close()

    return redirect( url_for('top' ) )

# Process sign in.
@application.route('/signin', methods=['POST'])
def signin():

    global url
    
    # Find sign in user.

    # Get login user's value from web form.
    login_id = request.form['login_id']
    in_pw = request.form['password']
    
    # Connect to database.
    db = connect_db()
    connect = db.cursor()

    # Find the user's id, username, and password.
    sql = 'select id, username, password from user where active_flg = 1 and login_id = %s'
    connect.execute( sql, [login_id] )
    result = connect.fetchall()

    # Disconnect form database.
    db.close()
    connect.close()
    
    # [Not equiped] If login_id is not found, show error page.
    
    user_id  = result[0][0]
    username = result[0][1]
    corr_pw  = result[0][2]

    if in_pw == corr_pw:
        # Publish session ID.
        publish_session( user_id, username, True )

        # Publish cookie.
        publish_cookie( redirect( url_for('top' ) ), login_id, password )

        # Redirect to top page with username.
        return redirect( url_for('top' ) )

    else:
        return render_template( 'error.html', message='パスワードが間違っています。' )

# Show top menu.
@application.route('/top', methods=['GET'])
def top():
    
    # Get login user's value from session.
    user_id = session['user_id']
    username = session['username']
                     
    # Connect to database.
    db = connect_db()
    connect = db.cursor()

    # Get users who are followed by login user.
    sql = 'select user_id from follow where active_flg = 1 and follower_id = %s'
    connect.execute( sql, [user_id] )
    result = connect.fetchall()

    # flw_id = [0] * len(result)
    flw_id = []
    
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
    
    
