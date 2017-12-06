from datetime import datetime
import os
from flask import Flask, request, render_template, redirect, session, url_for, make_response
import MySQLdb

application = Flask(__name__)

application.secret_key = os.urandom(24)

url_base = 'http://localhost:8080'
# url_base   = 'http://tukutter.test:8080'
# url_login  = '/static/login.html'
# url_login = '/static/test-page/signin.html'

# Connect to database.
def connect_db():
    
    db = MySQLdb.connect( user='root', passwd='YutaOkinawa1211', host='localhost', db='tukutter', charset='utf8')
    return db

# Publish session ID.
def publish_session( user_id, username, signin ):

    session['user_id']  = user_id
    session['username'] = username
    session['signin'] = True
    
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
        resp =  publish_cookie( url_base+'/top', login_id, in_pw )

        return resp

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

    # Get user's profile info includes image.
    sql = 'select prof_pict, username from user where id = %s'
    connect.execute( sql, [user_id] )
    user = connect.fetchall()

    print('Got "user"')
    print('user_id: ' + str(user_id))
    
    # Get users who are followed by login user.
    sql = 'select user_id from follow where active_flg = 1 and follower_id = %s'
    connect.execute( sql, [user_id] )
    temp = connect.fetchall()

    print('Got followed users')
    
    follow_id = []
    
    for num in range(len(temp)):
        # Get user id from result. 
        follow_id.append(temp[num][0])
                      
    follow_id.append(user_id)

    print('Made follow_id')
    
    view_name = username + '_top'

    # Get tweets as view.
    sql = ''
    
    for num in range(len(follow_id)-1):
        sql = sql + ' or user_id = %s'

    sql = sql + ' order by time desc'

    print(sql)
    print([view_name + str(follow_id)])
    connect.execute( sql, [view_name, follow_id] )
    # tweets = connect.fetchall()

    print('Created view')
    
    # Get user info related each tweets.
    sql = 'select user.prof_pict, user.username, %s.time, %s.content from user inner join %s on user.id = %s.user_id where user.id = %s'
    connect.execute( sql, [view_name, view_name, view_name, view_name, follow_id] )
    tweets = connect.fetchall()

    print('Got tweets')
    
    # Delete view.
    sql = 'drop view %s'
    connect.execute( sql, view_name )

    print('Deleted view')
    
    # Disconnect form database.
    db.close()
    connect.close()

    # str_tweet = 'tweet_id, user_id, content, time, </br>'
    # for tweet in tweets:
        # str_tweet = str_tweet + str(tweet[0]) + ', ' + str(tweet[1]) + ', ' + tweet[2] + ', ' + tweet[3].strftime('%Y/%m/%d %H:%M') + '</br>'
    # return str_tweet 

    return tweets[0][0]
    # return render_template( 'index.html', tweets=tweets )
    
    
