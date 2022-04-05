from datetime import datetime, timedelta
from flask import Flask, render_template, url_for, flash, redirect, request, session
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///uoft.db'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes = 10)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
class User(db.Model):
    __tablename__ = 'User'
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(20), unique=True, nullable = False)
    utorid = db.Column(db.Integer, unique=True, nullable = False)
    first = db.Column(db.String(20), nullable = False)
    last = db.Column(db.String(20), nullable = False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(20), nullable = False)
    type = db.Column(db.String(20), nullable = False)
   
    def __repr__(self):
        return f"User('{self.username}', '{self.email}')"

class Assessments(db.Model):
    __tablename__ = 'Assessments'
    id = db.Column(db.Integer, primary_key = True)
    assignmentName= db.Column(db.String(20), nullable = False)
    score = db.Column(db.REAL, nullable=False)
    out_of = db.Column(db.REAL, nullable=False)
    mark = db.Column(db.REAL, nullable=False)
    weighting = db.Column(db.REAL, nullable=False)
    student_username = db.Column(db.String(20), db.ForeignKey('User.username'), nullable = False)
    regrade = db.Column(db.Text, nullable=False)

    def __repr__(self):
        return f"Assessments('{self.student_username}', '{self.assignmentName}', '{self.mark}')"

class Feedback(db.Model):
    __tablename__ = 'Feedback'
    id = db.Column(db.Integer, primary_key = True)
    anonfeedback = db.Column(db.Text, nullable=False)
    instructor_username = db.Column(db.String(20), db.ForeignKey('User.username'), nullable = False)
    
    def __repr__(self):
        return f"Feedback('{self.instructor_username}', '{self.anonfeedback}')"


@app.route('/')
@app.route('/login', methods = ['GET','POST'])
def login():

    if request.method == 'GET':
        if 'person' in session:
            flash('Already Logged in')
            return redirect(url_for('index'))
        else:
            return render_template('login.html')
    else:
        
        username = request.form['Username']
        password = request.form['Password']

        person = User.query.filter_by(username = username).first()
    
        if not person or not bcrypt.check_password_hash(person.password, password):
            flash('Please check your login details and try again', 'error')
            return render_template('login.html')
        else:
         
            person_details = (
                username,
                person.type,
                person.first,
                person.last
            )

            session['person'] = person_details
            session.permanent = True
          
            return redirect(url_for('index')) 
@app.route('/index')
def index():
    pagename = 'home'
    return render_template('index.html', pagename = pagename)

@app.route('/lectures')
def lectures():
    pagename = 'lectures'
    return render_template('lectures.html', pagename = pagename)

@app.route('/assignments')
def assignments():
    pagename = 'assignments'
    return render_template('assignments.html', pagename = pagename)

@app.route('/feedback', methods = ['GET','POST'])
def feedback():
    if request.method == 'GET':
        all_instructors = query_instructor_user()
        return render_template('feedback.html', all_instructors = all_instructors)
    else:
        instructor = request.form['username']
        feedback = request.form['feedback']
        feedback_details = (
            feedback,
            instructor
        )
        add_feedback(feedback_details)
        flash('Your feedback has been sent to the Instructor')
        return redirect(url_for('grades'))

@app.route('/labs')
def labs():
    pagename = 'labs'
    return render_template('labs.html', pagename = pagename)

@app.route('/syllabus')
def syllabus():
    pagename = 'syllabus'
    return render_template('syllabus.html', pagename = pagename)

@app.route('/team')
def team():
    pagename = 'team'
    return render_template('team.html', pagename = pagename)

@app.route('/resources')
def resources():
    pagename = 'resources'
    return render_template('resources.html', pagename = pagename)

@app.route('/register', methods = ['GET','POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html')
    else:
        username = request.form['Username']
        first = request.form['first']
        last = request.form['last']
        email = request.form['Email']
        role = request.form['Type']
        utorid = request.form['utorid']
        person_by_user = User.query.filter_by(username = username).first()
        person_by_email = User.query.filter_by(email = email).first()
        person_by_utorid = User.query.filter_by(utorid = utorid).first()

        if person_by_user:
            flash('This username already exists', 'error')
            return render_template('register.html')
        if role == "":
            flash('Please choose a valid role', 'error')
            return render_template('register.html')
        if person_by_email:
            flash('This email already exists', 'error')
            return render_template('register.html')
        if person_by_utorid:
            flash('This utorid already exists', 'error')
            return render_template('register.html')
        
     

        print(role)
        print(person_by_email)
        print(person_by_user)


        hashed_password = bcrypt.generate_password_hash(request.form['Password']).decode('utf-8')
        reg_details = (
            username,
            email,
            hashed_password,
            role,
            first,
            last,
            utorid
        )
        add_user(reg_details)
        flash('Registration Successful! Please login now:')
        return redirect(url_for('login.html'))

@app.route('/studentGrades', methods = ['GET', 'POST'])
def studentGrades():
    
    if request.method == 'GET':
        query_assessment_result= query_assessment()
        print(query_assessment_result)
    
        return render_template('studentGrades.html',query_assessment_result = query_assessment_result)

@app.route('/grades', methods = ['GET', 'POST'])
def grades():
    if request.method == 'GET':
        query_assessment_result= query_assessment()
        print(query_assessment_result)
        return render_template('grades.html', query_assessment_result = query_assessment_result)

@app.route('/addgrades', methods = ['GET', 'POST'])
def addgrades():
    if request.method == 'GET':
        query_student_result = query_student_user()
        print(query_student_result)
        return render_template('addgrades.html',query_student_result = query_student_result)
    else:
        username = request.form['username']
        print(username)
        assignmentName = request.form['assignment']
        score = int(request.form['score'])
        out_of = int(request.form['out_of'])
        mark = round((score/out_of)*100, 2)
        
        weighting = request.form['weighting']
        grade_details = (
            assignmentName,
            score,
            out_of,
            mark,
            weighting,
            username
        )
        add_grades(grade_details)
        print(grade_details)
        message = username + "'s grade for "+ assignmentName +" has been added!"
        flash(message)
        return redirect(url_for('studentGrades'))
       

@app.route('/remark', methods = ['GET', 'POST'])
def remark():
    if request.method == 'GET':
        query_assessment_result= query_assessment()
        print(query_assessment_result)
        return render_template('remark.html', query_assessment_result = query_assessment_result)
    else:
        assignmentName = request.form['assignment']
        regrade = request.form['regrade']
        regrade_details = (
            assignmentName,
            regrade
        )
        add_regrade(regrade_details)
        flash("Your regrade request for " + assignmentName + " has been sent to the instructor!")
        return redirect(url_for('grades'))


@app.route('/viewfeedback', methods = ['GET', 'POST'])
def viewfeedback():
    if request.method == 'GET':
        query_feedback_result= query_feedback()
        return render_template('viewfeedback.html', query_feedback_result = query_feedback_result)

def query_assessment():
    user = session['person']
    print(user)
    if (user[1] == 'instructor'): 
        query_assessment = Assessments.query.all()
        sorting(query_assessment)
    else:
        query_assessment = Assessments.query.filter_by(student_username = user[0])
    print(query_assessment)
    
    return query_assessment

def query_feedback():
    user = session['person']
    if user[1] == 'instructor':
        query_feedback = Feedback.query.all()
        query_feedback = Feedback.query.filter_by(instructor_username = user[0])

        return query_feedback

def query_instructor_user():
    query_instructor = User.query.filter_by(type = 'instructor')
    return query_instructor

def query_student_user():
    query_student = User.query.all()
    query_student = User.query.filter_by(type = 'student')
    return query_student

def add_grades(grade_details):
    grade = Assessments(assignmentName = grade_details[0], score = grade_details[1], out_of = grade_details[2], mark = grade_details[3], weighting = grade_details[4], student_username = grade_details[5], regrade = "")
    db.session.add(grade)
    db.session.commit()
    print('success')

def add_user(reg_details):
    person = User(username = reg_details[0], utorid = reg_details[6], first = reg_details[4], last = reg_details[5], email = reg_details[1], password = reg_details[2], type = reg_details[3])
    db.session.add(person)
    db.session.commit()

def add_feedback(feedback_details):
    feedback = Feedback(anonfeedback = feedback_details[0],instructor_username = feedback_details[1])
    db.session.add(feedback)
    db.session.commit()

def add_regrade(regrade_details):
    user = session['person']
    changeRow = 0
    query_rows = Assessments.query.all()
    for rows in query_rows:
        if (rows.assignmentName == regrade_details[0] and rows.student_username == user[0]):
            changeRow = rows
    changeRow.regrade = regrade_details[1]
    db.session.commit()

@app.route('/logout')
def logout():
    session.pop('person', default = None)
    print(session)
    return redirect(url_for('index'))

def sorting(assessment_stuff):
    n = len(assessment_stuff)
 
    # Traverse through all array elements
    for i in range(n-1):
    # range(n) also work but outer loop will
    # repeat one time more than needed.
 
        # Last i elements are already in place
        for j in range(0, n-i-1):
 
            if assessment_stuff[j].student_username > assessment_stuff[j + 1].student_username :
                assessment_stuff[j], assessment_stuff[j + 1] = assessment_stuff[j + 1], assessment_stuff[j]
 


if __name__ == '__main__':
    app.run(debug=True)

