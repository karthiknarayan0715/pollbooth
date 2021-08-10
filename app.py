from flask import Flask, session, flash
from flaskext.mysql import MySQL
from flask import request
from models import User
app = Flask(__name__)
mysql = MySQL()
app.config['SECRET_KEY'] = 'Secret_Key'
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'Pass@1234'
mysql.init_app(app)
current_user = None
global user
user = None

def update_models():
    if 'logged_in' in session:
        global user 
        user = User(session['username'], session['email'], session['name'], session['role'])
def get_user():
    update_models()
    global user
    return user

import routes
