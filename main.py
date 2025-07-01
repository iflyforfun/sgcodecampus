from datetime import datetime
import time
import os
import random
from flask import Flask, redirect, render_template, request, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm.attributes import flag_modified
from flask_login import UserMixin, LoginManager, login_user, login_required, current_user, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
import pandas as pd
import plotly.express as px
from faker import Faker

app = Flask(__name__)
app.config['SECRET_KEY'] = 'SIL'
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'database.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)

db = SQLAlchemy(app)

class Admin(UserMixin, db.Model):
    id = db.Column(db.String, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(32), nullable=False)  
    age = db.Column(db.Integer, nullable=False)
    gender = db.Column(db.String(32), nullable=False)

    def __repr__(self):
        return f'<Admin {self.name}>'

class Nurse(UserMixin, db.Model):
    id = db.Column(db.String, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(1000), nullable=False)
    type = db.Column(db.String(100), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    gender = db.Column(db.String(32), nullable=False)
    race = db.Column(db.String(32), nullable=False)
    specialization = db.Column(db.String(100), nullable=True)
    experience = db.Column(db.String(200), nullable=True)
    reviews = db.Column(db.JSON, nullable=True, default=dict)

    def __repr__(self):
        return f'<Nurse {self.name}>'

class Job(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    admin_id = db.Column(db.String(100))
    title = db.Column(db.String(32), nullable=False)
    description = db.Column(db.String(500), nullable=False)
    job_scope = db.Column(db.String(32), nullable=False)
    pay = db.Column(db.String(32), nullable=False)
    shift_time = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now())
    applicants = db.Column(db.JSON, nullable=True, default=dict)

    completed = db.Column(db.Boolean, default=False)
    review = db.Column(db.String(500), nullable=True)
    rating = db.Column(db.Integer, nullable=True)

    def __repr__(self):
        return f'<Job ID: {self.id}>'

def populate_fake_jobs():
    fake_jobs = [
    {"title": "General Nurse", "description": "Assist with day-to-day healthcare needs in the community.", "job_scope": "Community Health", "pay": "3000", "shift_time": "9 AM - 5 PM"},
    {"title": "ICU Nurse", "description": "Provide critical care support to patients in the ICU.", "job_scope": "Critical Care", "pay": "4500", "shift_time": "Night Shift"},
    {"title": "Elder Care Nurse", "description": "Specialize in caring for the elderly population.", "job_scope": "Gerontology", "pay": "3500", "shift_time": "Morning Shift"},
    {"title": "Emergency Room Nurse", "description": "Deliver immediate care to emergency cases.", "job_scope": "Emergency", "pay": "5000", "shift_time": "12-hour Rotational"},
    {"title": "Public Health Nurse", "description": "Work on improving health outcomes at the community level.", "job_scope": "Community Health", "pay": "3200", "shift_time": "8 AM - 4 PM"},
    {"title": "Health Education Nurse", "description": "Educate individuals and families about healthy living practices.", "job_scope": "Community Health", "pay": "3100", "shift_time": "Flexible Hours"},
    {"title": "Home Care Nurse", "description": "Provide personalized healthcare to patients in their homes.", "job_scope": "Community Health", "pay": "3300", "shift_time": "9 AM - 6 PM"},
    {"title": "Outreach Program Nurse", "description": "Assist in health outreach and screening programs.", "job_scope": "Community Health", "pay": "2900", "shift_time": "7 AM - 3 PM"},
    {"title": "School Health Nurse", "description": "Promote health and wellness among school children.", "job_scope": "Community Health", "pay": "3100", "shift_time": "8 AM - 2 PM"},
    {"title": "Rehabilitation Nurse", "description": "Support patients recovering from injuries or surgeries.", "job_scope": "Community Health", "pay": "3500", "shift_time": "10 AM - 6 PM"},
    {"title": "Community Clinic Nurse", "description": "Assist with patient care in community clinics.", "job_scope": "Community Health", "pay": "3000", "shift_time": "9 AM - 5 PM"},
    {"title": "Preventive Care Nurse", "description": "Focus on preventive healthcare and lifestyle education.", "job_scope": "Community Health", "pay": "3400", "shift_time": "10 AM - 4 PM"},
    {"title": "Chronic Disease Management Nurse", "description": "Assist patients in managing chronic illnesses like diabetes.", "job_scope": "Community Health", "pay": "3600", "shift_time": "8 AM - 4 PM"},
    {"title": "Community Outreach Nurse", "description": "Work on community health campaigns and wellness programs.", "job_scope": "Community Health", "pay": "2900", "shift_time": "6 AM - 2 PM"},
    {"title": "Critical Care Nurse", "description": "Deliver advanced care to critically ill patients.", "job_scope": "Critical Care", "pay": "4800", "shift_time": "Night Shift"},
    {"title": "Neonatal ICU Nurse", "description": "Provide care for critically ill newborns in the NICU.", "job_scope": "Critical Care", "pay": "4600", "shift_time": "12-hour Rotational"},
    {"title": "Cardiac ICU Nurse", "description": "Specialize in caring for patients with severe cardiac conditions.", "job_scope": "Critical Care", "pay": "4700", "shift_time": "8 PM - 8 AM"},
    {"title": "Pediatric ICU Nurse", "description": "Deliver care to critically ill children.", "job_scope": "Critical Care", "pay": "4500", "shift_time": "Day Shift"},
    {"title": "Trauma ICU Nurse", "description": "Specialize in treating patients with traumatic injuries.", "job_scope": "Critical Care", "pay": "5000", "shift_time": "Night Shift"},
    {"title": "Neurosurgical ICU Nurse", "description": "Care for patients recovering from brain or spinal surgery.", "job_scope": "Critical Care", "pay": "4900", "shift_time": "12-hour Rotational"},
    {"title": "Burn ICU Nurse", "description": "Provide specialized care for burn patients.", "job_scope": "Critical Care", "pay": "4600", "shift_time": "8 AM - 8 PM"},
    {"title": "Post-Operative ICU Nurse", "description": "Deliver intensive care to post-surgery patients.", "job_scope": "Critical Care", "pay": "4700", "shift_time": "Rotating Shifts"},
    {"title": "Surgical ICU Nurse", "description": "Provide critical care for surgical patients.", "job_scope": "Critical Care", "pay": "4800", "shift_time": "Night Shift"},
    {"title": "Critical Care Float Nurse", "description": "Work across various ICU departments as needed.", "job_scope": "Critical Care", "pay": "5100", "shift_time": "12-hour Shifts"},
    {"title": "Geriatric Nurse", "description": "Focus on healthcare for elderly patients.", "job_scope": "Gerontology", "pay": "3700", "shift_time": "Day Shift"},
    {"title": "Palliative Care Nurse", "description": "Provide end-of-life care to elderly patients.", "job_scope": "Gerontology", "pay": "4000", "shift_time": "Night Shift"},
    {"title": "Dementia Care Nurse", "description": "Specialize in caring for patients with dementia.", "job_scope": "Gerontology", "pay": "3600", "shift_time": "Flexible Hours"},
    {"title": "Elderly Rehabilitation Nurse", "description": "Support elderly patients recovering from surgeries or illnesses.", "job_scope": "Gerontology", "pay": "3800", "shift_time": "8 AM - 4 PM"},
    {"title": "Assisted Living Nurse", "description": "Provide healthcare in assisted living facilities.", "job_scope": "Gerontology", "pay": "3500", "shift_time": "9 AM - 5 PM"},
    {"title": "Chronic Pain Management Nurse", "description": "Specialize in managing chronic pain in elderly patients.", "job_scope": "Gerontology", "pay": "3900", "shift_time": "10 AM - 6 PM"},
    {"title": "Elder Wellness Nurse", "description": "Promote healthy aging and wellness for the elderly.", "job_scope": "Gerontology", "pay": "3700", "shift_time": "8 AM - 2 PM"},
    {"title": "Hospice Care Nurse", "description": "Deliver compassionate care to terminally ill elderly patients.", "job_scope": "Gerontology", "pay": "4100", "shift_time": "Night Shift"},
    {"title": "Fall Prevention Nurse", "description": "Help elderly patients prevent falls and injuries.", "job_scope": "Gerontology", "pay": "3600", "shift_time": "10 AM - 4 PM"},
    {"title": "Memory Care Nurse", "description": "Focus on supporting elderly patients with memory impairments.", "job_scope": "Gerontology", "pay": "3800", "shift_time": "Morning Shift"},
    {"title": "ER Nurse", "description": "Provide immediate care to patients in the emergency room.", "job_scope": "Emergency", "pay": "5200", "shift_time": "12-hour Rotational"},
    {"title": "Trauma Nurse", "description": "Handle emergency trauma cases in the ER.", "job_scope": "Emergency", "pay": "5300", "shift_time": "Night Shift"},
    {"title": "Ambulance Nurse", "description": "Deliver emergency care during patient transportation.", "job_scope": "Emergency", "pay": "5100", "shift_time": "Flexible Shifts"},
    {"title": "Rapid Response Nurse", "description": "Respond to medical emergencies within the hospital.", "job_scope": "Emergency", "pay": "5000", "shift_time": "12-hour Shifts"},
    {"title": "Disaster Response Nurse", "description": "Assist during natural disasters and emergencies.", "job_scope": "Emergency", "pay": "5500", "shift_time": "On-Call"},
    {"title": "Emergency Triage Nurse", "description": "Prioritize patients based on the severity of their conditions.", "job_scope": "Emergency", "pay": "4800", "shift_time": "8 AM - 8 PM"},
    {"title": "Flight Nurse", "description": "Provide care during air ambulance evacuations.", "job_scope": "Emergency", "pay": "5600", "shift_time": "Rotational Shifts"},
    {"title": "Critical Response Nurse", "description": "Specialize in handling critical emergencies.", "job_scope": "Emergency", "pay": "5300", "shift_time": "12-hour Shifts"},
    {"title": "Shock Trauma Nurse", "description": "Care for patients in shock or severe trauma.", "job_scope": "Emergency", "pay": "5400", "shift_time": "Night Shift"},
    {"title": "Emergency Care Nurse", "description": "Deliver high-quality emergency care to patients.", "job_scope": "Emergency", "pay": "5200", "shift_time": "Day Shift"}
    ]

    for job in fake_jobs:
        new_job = Job(
            admin_id="1",  
            title=job["title"],
            description=job["description"],
            job_scope=job["job_scope"],
            pay=job["pay"],
            shift_time=job["shift_time"],
            created_at=datetime.now(),
            applicants={}
        )
        db.session.add(new_job)

    db.session.commit()
    print("Fake jobs added to the database.")

# with app.app_context():
#     db.drop_all()
#     db.create_all()
#     populate_fake_jobs()
#     print("Database reset and fake jobs populated.")


@login_manager.user_loader
def load_user(user_id):

    user_type = user_id[0]  

    if user_type == '0':  

        user = Nurse.query.filter_by(id=user_id).first()
    elif user_type == '1':  

        user = Admin.query.filter_by(id=user_id).first()
    else:

        return None

    return user

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/forgot-password')
def forgot_password():
    return render_template('forgot_password.html')

@app.route('/faqs')
def faqs():
    return render_template('faqs.html')

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user_type = request.form.get('user_type')
        email = request.form.get('email')
        password = request.form.get('password')
        remember = bool(request.form.get('remember'))

        if user_type == 'nurse':
            user = Nurse.query.filter_by(email=email).first()
        elif user_type == 'admin':
            user = Admin.query.filter_by(email=email).first()
        else:
            flash('Invalid user type selected')
            return redirect(url_for('login'))

        if not user or not check_password_hash(user.password, password):
            flash('Please check your login details and try again.')
            return redirect(url_for('login'))

        login_user(user, remember=remember)

        return redirect(url_for("index"))

    return render_template('login.html')

@app.route("/signup", methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        user_type = request.form['user_type']
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        dob = request.form['dob']  
        gender = request.form['gender']  
        specialization = request.form.get('specialization')  
        race = request.form.get('race')

        if password != confirm_password:
            flash('Passwords do not match.')
            return redirect(url_for('signup'))

        if user_type == 'nurse':
            existing_user = Nurse.query.filter_by(email=email).first()
        elif user_type == 'admin':
            existing_user = Admin.query.filter_by(email=email).first()
        else:
            flash('Invalid user type selected')
            return redirect(url_for('signup'))

        if existing_user:
            flash(f'An account with email {email} already exists.')
            return redirect(url_for('signup'))

        dob_date = datetime.strptime(dob, '%Y-%m-%d')
        today = datetime.today()
        age = today.year - dob_date.year - ((today.month, today.day) < (dob_date.month, dob_date.day))

        user_type_number = '0' if user_type == 'nurse' else '1'
        unix_timestamp = int(time.time())
        name_number = ''.join(str(ord(c)) for c in name)
        user_id = f"{user_type_number}{unix_timestamp}{name_number}"

        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')

        if user_type == 'nurse':
            new_user = Nurse(
                name=name,
                email=email,
                password=hashed_password,
                type=specialization,  
                race=race,
                age=age,
                gender=gender,
                reviews={}
            )
        elif user_type == 'admin':
            new_user = Admin(name=name, email=email, password=hashed_password,age=age,gender=gender)

        new_user.id = user_id  
        db.session.add(new_user)
        db.session.commit()

        flash(f'Your {user_type} account has been created! Please log in.')
        return redirect(url_for('login'))

    return render_template('signup.html')

@app.route('/job/<int:job_id>/apply', methods=['POST'])
@login_required
def apply_for_job(job_id):
    job = db.session.get(Job, job_id)
    if job:

        if current_user.id not in job.applicants:
            job.applicants[str(current_user.id)] = {
                'name': current_user.name,
                'type': current_user.type,
                'score': round(random.uniform(9.5,10.0),2),
                'status': 'applied'
            }
            flag_modified(job, "applicants")
            db.session.commit()
            flash('You have successfully applied for this job!', 'success')
        else:
            flash('You have already applied for this job.', 'warning')
    else:
        flash('Job not found.', 'danger')

    return redirect(url_for('view_job_details', job_id=job.id))

@app.route('/job/<int:job_id>/update_applicant_status/<applicant_id>', methods=['POST'])
@login_required
def update_applicant_status(job_id, applicant_id):
    job = Job.query.get(job_id)
    if not job or str(job.admin_id) != str(current_user.id):
        flash("You don't have permission to view applicants for this job.", "danger")
        return redirect(url_for('matches'))

    action = request.form.get('action')
    if action not in ['accept', 'reject']:
        flash('Invalid action.', 'danger')
        return redirect(url_for('view_job_details', job_id=job_id))

    if applicant_id in job.applicants:
        applicant = job.applicants[applicant_id]

        if action == 'accept':
            applicant['status'] = 'CONFIRMED'
        elif action == 'reject':
            applicant['status'] = 'REJECTED'

        flag_modified(job, "applicants")  
        db.session.commit()

        flash(f"Applicant {applicant['name']} has been {action}ed.", 'success')
    else:
        flash("Applicant not found.", 'danger')

    return redirect(url_for('view_job_details', job_id=job_id))

@app.route('/post_job', methods=['GET', 'POST'])
def post_job():
    if request.method == 'POST':
        if current_user.__class__.__name__ == 'Admin':

            title = request.form.get('title')
            job_scope = request.form.get('job_scope')
            description = request.form.get('description')
            pay = request.form.get('pay')
            shift_time = request.form.get('shift_time')

            job = Job(admin_id=current_user.id, title=title, job_scope=job_scope, description=description, pay=pay, shift_time=shift_time, applicants={})

            job = add_fake_nurses(job_scope,job)

            db.session.add(job)
            db.session.commit()

            flash('Job posted successfully!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Access denied: Only admins can post jobs.', 'danger')
            return redirect(url_for('dashboard'))
    return render_template('post_job.html')

def add_fake_nurses(specialization, job, count=10):
    """Generate and add fake nurses to the database."""
    fake_nurses = []
    fake = Faker()

    for _ in range(count):
        name = fake.name()
        email = fake.unique.email()
        password = fake.password()  
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')

        race = fake.random_element(elements=("Chinese", "Malay", "Indian", "Others"))
        gender = fake.random_element(elements=("Male", "Female"))
        dob = fake.date_of_birth(minimum_age=25, maximum_age=55)  

        today = datetime.today()
        age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))

        user_type_number = '0'  
        unix_timestamp = int(time.time())
        name_number = ''.join(str(ord(c)) for c in name)
        user_id = f"{user_type_number}{unix_timestamp}{name_number}"

        fake_nurses.append(Nurse(
            id=user_id,
            name=name,
            email=email,
            password=hashed_password,
            type=specialization,  
            race=race,
            age=age,
            gender=gender,
            reviews={}
        ))

    for nurse in fake_nurses:
        job.applicants[nurse.id] = {
            'name': nurse.name,
            'type': nurse.type,
            'score': round(random.uniform(8.0,10.0),2),
            'status': 'applied'
        }

    db.session.bulk_save_objects(fake_nurses)
    db.session.commit()

    return job

@app.route('/jobs', methods=['GET', 'POST'])
@login_required
def view_jobs():

    query = Job.query

    specialization_filter = request.args.get('specialization')
    if specialization_filter:
        query = query.filter(Job.job_scope.like(f'%{specialization_filter}%'))

    sort_by = request.args.get('sort_by', 'pay')
    if sort_by == 'pay':
        query = query.order_by(Job.pay.desc())  

    jobs = query.all()

    return render_template('jobs.html', jobs=jobs)

@app.route('/matches')
@login_required
def matches():

    jobs = Job.query.filter_by(admin_id=current_user.id).all()

    return render_template('matches.html', jobs=jobs)

@app.route('/job/<int:job_id>', methods=['GET'])
@login_required
def view_job_details(job_id):
    job = Job.query.get(job_id)
    job.applicants = dict(
    sorted(job.applicants.items(), key=lambda item: item[1]["score"], reverse=True))
    if job:
        return render_template('job_details.html', job=job)
    else:
        flash("Job not found.")
        return redirect(url_for('view_jobs'))

@app.route('/job/<int:job_id>/applicants', methods=['GET', 'POST'])
@login_required
def view_applicants(job_id):
    job = Job.query.get(job_id)
    if job.admin_id != current_user.id:
        flash("You don't have permission to view applicants for this job.", "danger")
        return redirect(url_for('matches'))

    if request.method == 'POST':

        applicant_name = request.form['applicant_name']
        action = request.form['action']  

        if applicant_name in job.applicants:
            status = 'accepted' if action == 'accept' else 'rejected'
            if job.applicant_status is None:
                job.applicant_status = {}

            job.applicant_status[applicant_name] = status
            db.session.commit()
            flash(f'{applicant_name} has been {status}.', 'success')
        else:
            flash("Applicant not found.", "danger")

    return render_template('applicants.html', job=job)

@app.route('/complete_job/<int:job_id>', methods=['GET', 'POST'])
@login_required
def complete_job(job_id):
    job = Job.query.get(job_id)
    if job and job.admin_id == current_user.id:
        applicant_id = request.args.get('applicant_id')  

        applicant_details = job.applicants.get(applicant_id)

        if not applicant_details:
            flash('Applicant not found.', 'danger')
            return redirect(url_for('matches'))

        if request.method == 'POST':

            job.completed = True
            db.session.commit()

            if applicant_details['status'] == 'CONFIRMED':
                review = request.form['review']
                rating = int(request.form['rating'])

                nurse = Nurse.query.get(applicant_id)
                if nurse:

                    nurse.experience = str(rating)

                    nurse.reviews[f"{len(nurse.reviews)}"] = review
                    flag_modified(nurse, "reviews")
                    db.session.delete(job)
                    db.session.commit()

                flash('Job completed and review submitted successfully.', 'success')
                return redirect(url_for('matches'))

        return render_template('complete_job.html', job=job, applicant_id=applicant_id, applicant_details=applicant_details)

    flash('Job not found or you do not have permission to complete this job.', 'danger')
    return redirect(url_for('matches'))

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("index"))

if __name__ == '__main__':
    app.run(debug=True)