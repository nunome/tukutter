from datetime import datetime
from flask import Flask, request, render_template, redirect, session, url_for, make_response
from werkzeug import secure_filename
import MySQLdb, os, random, string


url_base = 'http://localhost:8080'
upload_folder = './static/img'
allowed_extensions = set(['png','jpg'])

application = Flask(__name__)
application.secret_key = os.urandom(64)
application.config['UPLOAD_FOLDER'] = upload_folder

# Connect to database.
def connect_db():
    
    conn = MySQLdb.connect( user='root', passwd='YutaOkinawa1211', host='localhost', db='tukutter', charset='utf8')
    curs = conn.cursor()
    
    return ( conn, curs )

# Get user info.
def get_user( conn, curs ):

    user_id = session['user_id']
    
    # Get user's profile info includes image.
    sql = 'select prof_pict, username from user where id = %s'
    curs.execute( sql, [user_id] )
    user = curs.fetchall()

    return user
    
# Publish session ID.
def publish_session( user_id, username, signin ):

    session['user_id']  = user_id
    session['username'] = username
    session['signin']   = True
    
# Publish cookie.
def publish_cookie( link_to, login_id ):

    # Make response object.
    resp = make_response( redirect(link_to) )

    # Publish token.
    token = ''.join(random.choice(string.ascii_letters+string.digits) for i in range(128))

    # Store token.
    conn, curs = connect_db()

    sql = 'update user set token = %s where login_id = %s'
    curs.execute( sql, [token, login_id] )
    conn.commit()

    # Disconnect form database.
    conn.close()
    curs.close()    
    
    # Set cookie.
    max_age = 60*60*24 # 1day
    expires = int( datetime.now().timestamp() ) + max_age
    # path    = '/'
    # domain  = 'tukutter.test:8080'
    # secure  = None
    # httponly = False
    
    resp.set_cookie( 'login_id', login_id, max_age, expires )
    resp.set_cookie( 'token', token, max_age, expires )
    
    return resp

# Check image file extension.
def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1] in allowed_extensions

# Run this process before every route() function.
@application.before_request
def pre_request():

    global url_base
    
    # Consider signed in if 'True' at session.
    if session.get('signin'):
        return
    
    # No check if sign in/up/out page is requested.
    if request.path == '/signin' or \
       request.path == '/signup' or \
       request.path == '/signout':
        
        return

    cookie_lid = request.cookies.get( 'login_id', '' )
    
    if cookie_lid == '':
        # Redirect to sign in page.
        return redirect( url_base + '/signin' )
    
    else:
        # Collate password
        cookie_token = request.cookies.get( 'token' )

        # Connect to database.
        conn, curs = connect_db()

        # Find the user's id, username, and password.
        sql = 'select id, username, token from user where active_flg = 1 and login_id = %s'
        curs.execute( sql, [cookie_lid] )
        result = curs.fetchall()

        # Disconnect form database.
        conn.close()
        curs.close()
        
        user_id  = result[0][0]
        username = result[0][1]
        token    = result[0][2]
        
        if cookie_token == token:
            # Publish session ID.
            publish_session( user_id, username, True )
            
            # Redirect to requested page.
            return

        else:
            # Redirect to sign in page.
            return redirect( url_base + '/sign' )

# Redirect access from root to sign in page.
@application.route('/')
def root_access():

    global url_base
    
    # Redirect to signin page.
    return redirect( url_base + '/signin' )

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
    conn, curs = connect_db()

    # Add new user to "user" table.
    sql = 'insert into user( login_id, password, username ) value ( %s, %s, %s )'
    curs.execute( sql, [ login_id, password, username ] )
    conn.commit()
    
    # Get user_ID from SQL server.
    sql = 'select id from user where active_flg = 1 and login_id = %s'
    curs.execute( sql, [login_id] )
    user_id = curs.fetchall()[0][0]
    
    # Publish session ID.
    publish_session( user_id, username, True )

    # Publish cookie.
    resp = publish_cookie( url_base+'/top', login_id )
    
    # Disconnect form database.
    conn.close()
    curs.close()

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
    conn, curs = connect_db()

    # Find the user's id, username, and password.
    sql = 'select id, username, password from user where active_flg = 1 and login_id = %s'
    curs.execute( sql, [login_id] )
    result = curs.fetchall()

    # Disconnect form database.
    conn.close()
    curs.close()
    
    # [Not equiped] If login_id is not found, show error page.
    
    user_id  = result[0][0]
    username = result[0][1]
    corr_pw  = result[0][2]

    if in_pw == corr_pw:
        # Publish session ID.
        publish_session( user_id, username, True )
        
        # Publish cookie then link to '/top'.
        resp =  publish_cookie( url_base + '/top', login_id )

        return resp

    else:
        return render_template( 'error.html', message='パスワードが間違っています。' )

# Process sign out.
@application.route('/signout')
def signout():

    global url_base

    # Clear token at database.

    # Connect database.
    conn, curs = connect_db()

    sql = 'update user set token = \'\' where id = %s'
    curs.execute( sql, [session['user_id']] )
    conn.commit()
    
    # Disconnect form database.
    conn.close()
    curs.close()
    
    # Close session.
    session.pop( 'username',    '' )
    session.pop( 'user_id',     '' )
    session.pop( 'signin',   False )
    
    # Clear cookie then redirect to sign in page.
    resp = make_response( redirect( url_base + '/signin' ) )
    resp.set_cookie( 'login_id', '' )
    resp.set_cookie( 'token',    '' )

    return resp

# Edit profile.
@application.route('/profile_edit', methods=['GET', 'POST'])
def prof_edit():

    global url_base, upload_folder
    
    if request.method == 'GET':
        # Show profile edit page.
        return render_template( 'profile_edit.html' )
    
    user_id  = session['user_id']
    
    # Get new user's value from web form.
    login_id = request.form['login_id']
    new_pw1  = request.form['password']
    new_pw2  = request.form['conf_password']
    username = request.form['username']
    profile  = request.form['profile']
    img_file = request.files['img_file']
    
    if login_id:
        return render_template( 'error.html', message='login_id は変更できません。' )
    
    if new_pw1 != new_pw2:
        return render_template( 'error.html', message='パスワードが一致していません。' )

    # Connect database.
    conn, curs = connect_db()

    # Change password.
    if new_pw1:
        sql = 'update user set password = %s where id = %s'
        curs.execute( sql, [new_pw1, user_id] )

    # Change username.
    if username:
        sql = 'update user set username = %s where id = %s'
        curs.execute( sql, [username, user_id] )
        session.pop['username', username]
        
    # Change profile.
    if profile:
        sql = 'update user set profile = %s where id = %s'
        curs.execute( sql, [profile, user_id] )
    
    # Upload profile image.
    if img_file and allowed_file(img_file.filename):
        filename = secure_filename(img_file.filename)
        img_file.save( os.path.join(application.config['UPLOAD_FOLDER'], filename) )

        sql = 'update user set prof_pict = %s where id = %s'
        curs.execute( sql, [upload_folder[1:]+'/'+filename, user_id] )

    # Commit connect.
    conn.commit()
    
    # Disconnect from database.
    conn.close()
    curs.close()
    
    return redirect( url_base + '/profile/' + session['username'] )

# Show top menu.
@application.route('/top')
def top():
    
    # Get login user's value from session.
    user_id  = session['user_id']
    username = session['username']
                     
    # Connect to database.
    conn, curs = connect_db()

    # Get user's profile info includes image.
    user = get_user( conn, curs )
    
    # Get tweets.
    sql = ( 'select user.prof_pict, user.username, tweet.time, tweet.content ' +
            'from follow ' +
            'inner join tweet on follow.user_id = tweet.user_id ' +
            'inner join user on user.id = tweet.user_id ' +
            'where follow.follower_id = %s ' +
            'order by tweet.time desc' )
    
    curs.execute( sql, [user_id] )    
    tweets = curs.fetchall()

    # Disconnect from database.
    conn.close()
    curs.close()

    return render_template( 'index.html', user=user, tweets=tweets )

# Show profile page.
@application.route('/profile')
def redirect_profile():

    global url_base
    
    return redirect( url_base + '/profile/' + session['username'] )
    
@application.route('/profile/<in_name>')
def profile(in_name):

    ## [Need to handle when in_name is empty.]
    
    global url_base
    
    # Get login user's value from session.
    user_id  = session['user_id']
    username = session['username']
        
    # Connect to database.
    conn, curs = connect_db()

    # Get user's profile info includes image.
    user = get_user( conn, curs )
    
    # Get requested user's profile and tweets.
    sql = 'select prof_pict, username, profile, id from user where username = %s'
    curs.execute( sql, [in_name] )
    disp_user = curs.fetchall()

    sql = ( 'select user.prof_pict, user.username, tweet.time, tweet.content, tweet.id ' +
            'from user ' +
            'inner join tweet on tweet.user_id = user.id ' +
            'where tweet.user_id = %s ' +
            'order by tweet.time desc' )
    curs.execute( sql, [disp_user[0][3]] )
    tweets = curs.fetchall()

    # Disconnect from database.
    conn.close()
    curs.close()

    ## [Need to add function to distingush follow or not and requested user is as signin user or not]
    ## In case of requested to show signin user.
    # if in_name == username:
        ## Jump as login user.
        
    return render_template( 'profile.html', user=user, disp_user=disp_user, tweets=tweets )
    

@application.route('/tweet', methods=['GET', 'POST'])
def tweet():

    global url_base

    # Get login user's value from session.
    user_id  = session['user_id']
    username = session['username']
                     
    # Connect to database.
    conn, curs = connect_db()

    # Get user's profile info includes image.
    user = get_user( conn, curs )

    # Show tweet form page.
    if request.method == 'GET':
        # Show profile edit page.
        return render_template( 'tweet.html', user=user )

    # Get tweet content.
    tweet = request.form['tweet']

    # Insert new tweet.
    sql = 'insert into tweet(content, user_id) values(%s,%s)'
    curs.execute( sql, [tweet, user_id] )
    conn.commit()

    # Disconnect from database.
    conn.close()
    curs.close()

    # Redirect to profile page.
    return redirect( url_base + '/profile/' + username )

# Edit tweet.
@application.route('/tweet_edit/<tweet_id>')
def tweet_edit(tweet_id):

    pass

# Search words in tweet.
@application.route('/search', methods=['GET','POST'])
def search():

    global url_base
            
    # Connect database.
    conn, curs = connect_db()

    # Get user info.
    user = get_user( conn, curs )

    if request.method == 'GET':
        return render_template( 'search.html', user=user, tweets='' )

    # Get search word from the form.
    word = request.form['word']

    print(word)
    # Get tweets including search word.
    sql = ( 'select user.prof_pict, user.username, tweet.time, tweet.content ' +
            'from user ' +
            'inner join tweet on tweet.user_id = user.id ' +
            'where tweet.content like %s ' +
            'order by tweet.time desc' )
    curs.execute( sql, [('%'+word+'%')] )
    tweets = curs.fetchall()

    print(tweets)
    return render_template( 'search.html', user=user, tweets=tweets )


