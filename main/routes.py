import secrets
import os
from tkinter import Variable
from flask import render_template, url_for, flash, redirect, request
from matplotlib.style import use
from main import app, db, bcrypt
from main.forms import RegistrationForm, LoginForm, UpdateAccountForm
from main.models import User, Tracker, Inputaken
from flask_login import login_user, current_user, logout_user, login_required
from PIL import Image
from sqlalchemy import exc
from main.chart import *


@app.route("/")
def home():
    return render_template("home.html")

@app.route("/track", methods=['GET', 'POST'])
@login_required
def track():
    if request.method == 'POST':
        title = request.form['track_variable']
        variable = request.form['track_type']
        if(title == 'Select option' or variable == 'Select option'):
            flash('Please select a valid option', 'danger')
            return redirect(url_for('track'))
        else:
            task_table = Tracker(tracker_name=title,
                                 task_value_type=variable, user_id=current_user.id)
        user = Tracker.query.filter(Tracker.user_id == current_user.id).all()                        
        if len(user)!=0:
            for i in user:
                if str(i)!=title:
                    try:
                        db.session.add(task_table)
                        db.session.commit()
                    except exc.IntegrityError:
                        db.session.rollback()
                else:
                    return redirect(url_for('track'))
        else:
            db.session.add(task_table)
            db.session.commit()             
            
     
    user = User.query.filter_by(id=current_user.id).first()
    outputpage = user.trackers
    outputpage=Tracker.query.filter_by(user_id=current_user.id).all()
    if(len(outputpage) == 0):
        return render_template("track.html", title="Track")
    return render_template('track.html', outpage=outputpage)


@app.route("/track/delete/<int:sno>")
@login_required
def track_delete(sno):
    task_table = Tracker.query.filter_by(sno=sno).first()
    db.session.delete(task_table)
    db.session.commit()
    return redirect("/track")


@app.route("/log/<int:sno>", methods=['GET', 'POST'])
@login_required
def log(sno):
    task_table = Tracker.query.filter_by(sno=sno).first()
    if request.method == 'POST':
        title = request.form['title']
        value = request.form['value']
        variable = task_table.task_value_type
        if(title == '' or value == ''):
            flash('please enter valid values','danger')
            return redirect(url_for('log', sno=sno))
        else:
            log_table = Inputaken(task_title=title, task_value=value, task_variable=variable,
                                  user_id=current_user.id, tracker_id=task_table.sno)
            db.session.add(log_table)
            db.session.commit()
            return redirect("/log/" + str(task_table.sno))
    outputpage = Inputaken.query.filter_by(
        tracker_id=sno, user_id=current_user.id).all()
    return render_template('log.html', task=task_table, outputpage=outputpage)


@app.route("/log/update/<int:sno>", methods=['GET', 'POST'])
@login_required
def log_update(sno):
    if request.method == 'POST':
        title = request.form['title']
        value = request.form['value']
        task_table = Inputaken.query.filter_by(sno=sno).first()
        task_table.task_title = title
        task_table.task_value = value
        db.session.add(task_table)
        db.session.commit()
        return redirect("/log/"+str(task_table.tracker_id))
    task_table = Inputaken.query.filter_by(sno=sno).first()
    return render_template('updatelog.html', taskupdate=task_table)


@app.route("/log/delete/<int:sno>")
@login_required
def log_delete(sno):
    task_table = Inputaken.query.filter_by(sno=sno).first()
    db.session.delete(task_table)
    db.session.commit()
    return redirect("/log/"+str(task_table.tracker_id))


@app.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(
            form.password.data).decode('utf-8')
        user = User(username=form.username.data,
                    email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash(f'Account created for {form.username.data}!', 'success')
        return redirect(url_for('login'))
    return render_template("register.html", title='Register', form=form)


@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Please check username and password', 'danger')
    return render_template("login.html", title='Login', form=form)


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))


@app.route("/log/dashboard/<int:sno>")
@login_required
def dashboard(sno):
    tracker_stats = Inputaken.query.filter_by(tracker_id=str(sno)).all()
    if type(tracker_stats[1].task_value) == str:
            pie_chart(tracker_stats)       
    else:
            line_plot(tracker_stats)
    return render_template("chart.html")


def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/images', picture_fn)
    output_size = (125, 125)
    image = Image.open(form_picture)
    image.thumbnail(output_size)
    image.save(picture_path)

    return picture_fn

@app.route("/account", methods=['GET', 'POST'])
@login_required
def account():
    image_file = url_for('static', filename='images/' +
                         current_user.image_file)
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash('Your account has been updated!', 'success')
        return redirect(url_for('account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    return render_template("account.html", title="Account", image_file=image_file, form=form)
