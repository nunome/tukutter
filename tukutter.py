from datetime import datetime
import os
from flask import Flask, request, render_template, redirect, session, url_for, make_response
import MySQLdb

application = Flask(__name__)

application.secret_key = os.urandom(24)

url_base = 'http://localhost:8080'

# Connect to database.
def connect_db():
    
    db = MySQLdb.connect( user='root', passwd='YutaOkinawa1211', host='localhost', db='tukutter', charset='utf8')
    return db

# Publish session ID.
def publish_session( user_id, username, signin ):

    session['user_id']  = user_id
    session['username'] = username
    session['signin']   = True
    
# Publish cookie.
def publish_cookie( link_to, login_id, password ):

    resp = make_response( redirect(link_to) )
    
    max_age = 60*60*24 # 1day
    expires = int( datetime.now().timestamp() ) + max_age
    # path    = '/'
    # domain  = 'tukutter.test:8080'
    # secure  = None
    # httponly = False
    
    resp.set_cookie( 'login_id', login_id, max_age, expires )
    resp.set_cookie( 'password', password, max_age, expires )
    
    return resp

# Run this process before every route() function.
@application.before_request
def pre_request():

    global url_base
    
    # Consider signed in if 'True' at session.
    if session.get('signin'):
        return
    
    # No check if sign in page is requested.
    if request.path == '/signin' or request.path == '/signup':
        return

    cookie_lid = request.cookies.get( 'login_id', None )
    
    if cookie_lid == None:
        # Redirect to sign in page.
        return redirect( url_base + '/signin' )
    
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
            return redirect( url_base + url_login )

# Redirect access from root to sign in page.
@application.route('/')
def root_access():

    global url_base
    
    # Redirect to login page.
    return redirect( url_base+'/top' )

# Add new user.
@application.route('/signup', methods=['POST','GET'])
def signup():

    global url_base

    if request.method == 'GET':
        # Show sign up page.
        return render_template( 'signup.html' ) 
    
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
    connect.execute( sql, [login_id] )
    user_id = connect.fetchall()[0][0]
    
    # Publish session ID.
    publish_session( user_id, username, True )

    # Publish cookie.
    resp = publish_cookie( url_base+'/top', login_id, password )
    
    # Disconnect form database.
    db.close()
    connect.close()

    return resp

# Process sign in.
@application.route('/signin', methods=['POST','GET'])
def signin():

    global url_base

    if request.method == 'GET':
        # Show sign in page.
        return render_template( 'signin.html' )
    
    # Find sign in user.

    # Get login user's value from web form.
    login_id = request.form['login_id']
    in_pw    = request.form['password']
    
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
        
        # Publish cookie then link to '/top'.
        resp =  publish_cookie( url_base + '/top', login_id, in_pw )

        return resp

    else:
        return render_template( 'error.html', message='パスワードが間違っています。' )

# Process sign out.
@application.route('/signout')
def signout():

    global url_base

    # Close session.
    session.pop( 'username',  None )
    session.pop( 'user_id',   None )
    session.pop( 'signin',   False )
    
    # Clear cookie then redirect to sign in page.
    resp =make_response( redirect( url_base + '/signin' ) )
    resp.set_cookie( 'login_id', None )
    resp.set_cookie( 'password', None )

    return resp
    
# Show top menu.
@application.route('/top')
def top():
    
    # Get login user's value from session.
    user_id  = session['user_id']
    username = session['username']
                     
    # Connect to database.
    db = connect_db()
    connect = db.cursor()

    # Get user's profile info includes image.
    sql = 'select prof_pict, username from user where id = %s'
    connect.execute( sql, [user_id] )
    user = connect.fetchall()
    
    # Get tweets.
    sql = ( 'select user.prof_pict, user.username, tweet.time, tweet.content ' +
            'from follow ' +
            'inner join tweet on follow.user_id = tweet.user_id ' +
            'inner join user on user.id = tweet.user_id ' +
            'where follow.follower_id = %s ' +
            'order by tweet.time desc' )
    
    connect.execute( sql, [user_id] )    
    tweets = connect.fetchall()

    # Disconnect form database.
    db.close()
    connect.close()

    return render_template( 'index.html', user=user, tweets=tweets )
    
@application.route('/profile_edit', methods=['GET', 'POST'])
def prof_edit():

    if request.method == 'GET':
        # Show profile edit page.
        return render_template( 'profile_edit.html' )

    user_id  = session['user_id']
    username = session['username']
    
    # Get new user's value from web form.
     # login_id = request.form['login_id']
    new_pw1  = request.form['password']
    new_pw2  = request.form['conf_password']
    username = request.form['username']

    if new_pw1 != new_pw2:
        return render_template( 'error.html', message='パスワードが一致していません。' )

    if len(new_pw1) != 0:
        sql = 'update password 
    
    print(username)
    print(new_pw1)
    
    return render_template( 'profile.html' )

