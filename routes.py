from models import Poll, Teams
from flask import redirect, request, session
from flask.helpers import flash, url_for
from flask.templating import render_template
from pymysql.cursors import DictCursor
from app import app, mysql, update_models, get_user
option=0
#ROUTE: LOGIN
@app.route("/login", methods = ['GET', 'POST'])
def login():
    if "logged_in" in session and "role" in session:
        if(session['logged_in'] == True):
            return redirect(url_for('home'))
    username = ''
    password = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form.get('username')
        password = request.form.get('password')
        if not check_username(username) or not check_password(password):
            flash('invalid input, Only a-z, 0-9 and _ is allowed')
            return redirect('/login')
        conn = mysql.connect()
        cursor = conn.cursor(DictCursor)
        cursor.execute('USE mydatabase;')
        cursor.execute('SELECT * FROM users WHERE username = %s AND password = %s', (username, password))
        account = cursor.fetchone()
        if account:
            session['logged_in'] = True
            session['id'] = account.get('id')
            session['username'] = account.get('username')
            session['passwd'] = account.get('password')
            session['email'] = account.get('email')
            session['name'] = account.get('name')
            session['role'] = account.get('role')
            session['teams'] = account.get('teams')
            update_models()
            return redirect(url_for('home'))
        else:
            flash("Incorrect username or password")

        
    return render_template('login.html')


#ROUTE: REGISTER
@app.route("/register", methods = ['POST', 'GET'])
def register():
    if "logged_in" in session and "role" in session:
        if(session['logged_in'] == True):
            return redirect(url_for('home'))
    username = ''
    password = ''
    password2 = ''
    email = ''
    name = ''
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        password2 = request.form.get('password2')
        email = request.form.get('email')
        name = request.form.get('name')
        if not check_username(username) or not check_password(password) or not check_password(password2) or not check_input(email) or not check_input(name):
            flash('invalid inputs')
            return redirect('/register')
        if username and password and password2 and email and name:
            if password == password2:
                conn = mysql.connect()
                cursor = conn.cursor(DictCursor)
                cursor.execute('USE mydatabase')
                cursor.execute('SELECT * FROM users WHERE username= %s ', str(username))
                if(cursor.fetchone() == None):
                    cursor.execute('INSERT INTO users (username, password, email, name, role, teams) VALUES (%s, %s, %s, %s, %s, %s)', (username, password, email, name, "user", "_none_"))
                    conn.commit()
                    cursor.close()
                    flash('Your account has been created pls login now')
                    return redirect(url_for('login'))
                else:
                    flash("Uhmm username already exists, pls try something else")
                    return redirect(url_for('register'))
            else: 
                flash('password and repeat password dont match, pls check')
        else:
            flash('fill the form!')
    return render_template('register.html')


#ROUTE: LOGOUT
@app.route("/logout")
def logout():
    session['logged_in'] = False
    session.pop('username', None)
    return redirect(url_for('login'))


#ROUTE: ADMIN
@app.route("/admin")
def admin():
    return render_template('admin.html', title="Admin")


#ROUTE: CREATE NEW TEAM
@app.route("/create_new_team", methods = ['POST', 'GET'])
def create_team():
    if is_admin():
        if request.method == "POST":
            teamname = request.form.get('teamname')
            password = request.form.get('password')
            password2 = request.form.get('password2')
            if(password == password2):
                conn = mysql.connect()
                cur = conn.cursor()
                cur.execute('USE mydatabase')
                cur.execute('INSERT INTO teams(name, password) VALUES (%s, %s)', (teamname, password))
                conn.commit()
                cur.close()
        return render_template('newteam.html', title="Create Teams")
    else:
        flash('Not accessible')
        return redirect(url_for('home'))


#To create a poll
@app.route("/create_new_poll", methods = ['GET', 'POST'])
def createpoll():
    global option
    if not is_admin():
        flash('Access denied')
        return redirect(url_for('home'))
    else:
        if request.method == 'POST':
            if request.form.get('addoption'):
                option = option+1
                return render_template('createpoll.html', option = option)
            if request.form.get('removeopt'):
                option = option-1
                return render_template('createpoll.html', option = option)
            if request.form.get('submit'):
                form = request.form
                title = form.get('title')
                question = form.get('question')
                team_id = form.get('team_id')
                options = []
                for i in range(option):
                    options.append(form.get('option-'+str(i+1)))
                if len(options) < 3:
                    flash('you need atleast 3 options for a valid poll!!')
                elif not (check_input(title) and check_input(question) and [check_input(option) for option in options]):
                    flash('invalid input!')
                else:
                    conn = mysql.connect()
                    cur = conn.cursor(DictCursor)
                    cur.execute('USE mydatabase')
                    cur.execute('SELECT * FROM teams where id=%s', (team_id))
                    if cur.fetchone():
                        option_to_table = ''
                        for opt in options:
                            if(options.count(opt)>1):
                                flash('Repeating options! A poll must have unique options')
                                return redirect(url_for('createpoll'))
                            option_to_table = option_to_table + opt + '|'
                        cur.execute('INSERT INTO polls(title, question, options) VALUES(%s,%s,%s);',(title, question, option_to_table))
                        poll_id = cur.lastrowid
                        cur.execute('INSERT INTO polls_team(team_id, poll_id) VALUES(%s,%s)',(team_id, poll_id))
                        conn.commit()
                        cur.close()
                    else:
                        flash('Uhm.. Looks like the team doesnt exist!')
        return render_template('createpoll.html', option = option)


#To end a poll
@app.route("/end_poll", methods=['GET', 'POST'])
def endpoll():
    if not is_admin():
        return "ACCESS DENIED"
    conn = mysql.connect()
    cur = conn.cursor(DictCursor)
    cur.execute('USE mydatabase')
    cur.execute('SELECT * FROM polls')
    polls = cur.fetchall()
    if request.method == 'POST':
        for poll in polls:
            if request.form.get('end.'+str(poll['id'])):
                cur.execute('UPDATE polls SET is_ended=True WHERE id=%s',(poll['id']))
                conn.commit()
                flash('Poll '+poll['title']+' has now ended')
                return redirect(url_for('endpoll'))
    return render_template('endpoll.html', polls = polls)


#View the results of a poll
@app.route("/view_poll")
def viewpoll():
    conn = mysql.connect()
    cur = conn.cursor(DictCursor)
    cur.execute('USE mydatabase')
    cur.execute('SELECT * FROM polls')
    polls_sql = cur.fetchall()
    polls = []
    results = {}
    for poll in polls_sql:
        id = poll['id']
        title = poll['title']
        question = poll['question']
        options = poll['options'].split('|')
        is_ended = poll['is_ended']
        polls.append(Poll(id, title, question, options, is_ended))
        result = {}
        cur.execute('SELECT * FROM poll_users WHERE poll_id=%s', (id))
        poll_votes = cur.fetchall()
        for vote in poll_votes:
            if vote.get('options') in result:
                result[vote.get('options')] = result[vote.get('options')] + 1
            else:
                result[vote.get('options')] = 1
        results[id] = result
    return render_template('poll_results.html', polls = polls, result = results)


#ROUTE: HOME
@app.route("/")
@app.route("/home")
def home():
    if "logged_in" in session and "role" in session:
        if session["logged_in"] == True and session["role"] == "user":
            conn  =mysql.connect()
            cur = conn.cursor(DictCursor)
            cur.execute('USE mydatabase')
            cur.execute('SELECT team_id FROM teams_users WHERE user_id=%s', (session['id']))
            team_ids = cur.fetchall()
            teams = []
            for team_id in team_ids:
                cur.execute('SELECT * FROM teams WHERE id=%s', team_id.get('team_id'))
                team = cur.fetchone()
                new_team = Teams(team.get('id'), team.get('name'))
                teams.append(new_team)
            return render_template('home.html', teams = teams, user = get_user())
        elif session["logged_in"] == True and is_admin:
            return redirect(url_for('admin'))
        else:
            return redirect(url_for('login'))

    else:
        return redirect(url_for('login'))


#ROUTE: JOIN A NEW TEAM
@app.route("/join_team", methods = ['GET', 'POST'])
def jointeam():
    if not is_admin():
        if request.method == 'POST':
            form = request.form
            team_id = str(form.get('team_id'))
            team_password = form.get('team_password')
            conn = mysql.connect()
            cur = conn.cursor()
            cur.execute('USE mydatabase')
            cur.execute('SELECT * FROM teams_users WHERE user_id=%s and team_id=%s', (session['id'], team_id))
            if not cur.fetchone()==None:
                flash('Looks like you are already in the team!')
            else:
                cur.execute('SELECT * FROM teams WHERE id=%s and password=%s', (team_id, team_password))
                existing_team = cur.fetchone()
                if not existing_team == None:
                    cur.execute('INSERT INTO teams_users(team_id, user_id) values (%s,%s);', (team_id, session['id']))
                    conn.commit()
                    cur.close()
                else:
                    flash('invalid team id or password!')
                    return redirect(url_for('home'))
        user = get_user()
        return render_template('jointeam.html', user = user)
    else: 
        flash("Access denied")
        return redirect(url_for('admin'))


#teams home page
@app.route("/team<team_id>")
def team_page(team_id):
    conn = mysql.connect()
    cur = conn.cursor(DictCursor)
    cur.execute('USE mydatabase')
    cur.execute('SELECT * FROM teams_users WHERE team_id=%s and user_id=%s',(team_id, session['id']))
    print(session['id'])
    if cur.fetchone()==None:
        return render_template("errorpage.html", error="Team does not exist (or) Access denied")
    else:
        cur.execute('SELECT * FROM teams WHERE id=%s', (team_id))
        team_name = cur.fetchone().get('name')
        cur_team = Teams(team_id, team_name)
        cur.execute('SELECT poll_id FROM polls_team WHERE team_id=%s',(team_id))
        poll_ids_str = cur.fetchall()
        polls = []
        for poll in poll_ids_str:
            id = poll.get('poll_id')
            cur.execute('SELECT * FROM polls WHERE id=%s', (id))
            from_sql = cur.fetchone()
            newpoll = Poll(from_sql.get('id'), from_sql.get('title'), from_sql.get('question'), from_sql.get('options').split('|'), from_sql.get('is_ended'))
            polls.append(newpoll)
        return render_template('teampage.html', team = cur_team, user = get_user(), polls = polls)


#To view and answer a poll
@app.route("/poll<poll_id>", methods = ['GET', 'POST'])
def poll_page(poll_id):
    conn = mysql.connect()
    cur = conn.cursor(DictCursor)
    cur.execute('USE mydatabase')
    cur.execute('SELECT * FROM polls WHERE id=%s', (poll_id))
    sql_val = cur.fetchone()
    poll = Poll(sql_val.get('id'), sql_val.get('title'), sql_val.get('question'), sql_val.get('options').split('|'), sql_val.get('is_ended'))
    cur.execute('SELECT * FROM poll_users WHERE user_id=%s AND poll_id=%s',(session['id'], poll.id))
    user_response = cur.fetchone()
    user_responded = False
    if user_response==None:
        user_responded = False
    else:
        user_responded = True
    if poll.is_ended == "False" and not user_responded:
        if request.method == "POST":
            form = request.form
            selected_option = form.get('option')
            cur.execute('INSERT INTO poll_users (poll_id, user_id, options) VALUES (%s,%s,%s)',(poll.id, session['id'], selected_option))
            conn.commit()
            return redirect('/poll'+poll_id)
    return render_template('poll.html', user = get_user(), poll = poll, response = user_response)


def check_username(input):
    allowed = "abcdefghijklmnopqrstuvwxyz_0123456789"
    for i in input:
        if i not in allowed:
            return False
        return True


def check_password(input):
    allowed = "abcdefghijklmnopqrstuvwxyz_0123456789"
    for i in input:
        if i not in allowed:
            return False
        return True


#Checks the input entered by the user
def check_input(input):
    not_allowed = [' users', ' polls', ' poll_users', ' polls_team', ' teams_users', ' teams', '\\']
    for i in  input:
        if i in not_allowed:
            return False
    return True


#checks if the current user is an admin
def is_admin():
    if session["role"] == "admin":
        return True
    else:
        return False