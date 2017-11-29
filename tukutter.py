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

        return redirect( url + '/static/login.html' )

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

@application.route('/top', methods=['POST'])
def top():

    # Show top menu.

    # Find login user.
    
    login_id = request.form['login_id']
    password = request.form['password']
    
    

