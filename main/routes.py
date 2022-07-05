import secrets
import os
from flask import render_template, url_for, flash, redirect, request
from main import app, db, bcrypt
from main.forms import RegistrationForm, LoginForm, UpdateAccountForm
from main.models import User, Tracker,Inputaken
from flask_login import login_user, current_user, logout_user, login_required
from PIL import Image
from sqlalchemy import exc


@app.route("/")
def home():
    return render_template("home.html")

@app.route("/track", methods=['GET', 'POST'])
@login_required
def track():
    if request.method == 'POST':
        title = request.form['track_variable']
        variable = request.form['track_type']
        task_table = Tracker(tracker_name=title, task_value_type=variable)
        if task_table not in db.session:
            try:
                db.session.add(task_table)
                db.session.commit()
            except exc.IntegrityError:
                db.session.rollback()
        else:
            return redirect("/track")
    outputpage = Tracker.query.all()
    return render_template('track.html', outpage=outputpage)

@app.route("/track/delete/<int:sno>")
@login_required
def track_delete(sno):
    task_table=Tracker.query.filter_by(sno=sno).first()
    db.session.delete(task_table)
    db.session.commit()
    return redirect("/track")  

@app.route('/log', methods=['GET','POST'])
@login_required
def log():
    if request.method=='POST':
        title=request.form['title']
        value=request.form['value']
        variable=request.form['variable']
        task_table=Inputaken(task_title=title,task_value=value,task_variable=variable)
        db.session.add(task_table)
        db.session.commit()
    outputpage=Inputaken.query.all()
    return render_template('log.html',outputpage=outputpage)    

@app.route("/log/update/<int:sno>", methods=['GET', 'POST'])
@login_required
def log_update(sno):
    if request.method=='POST':
        title=request.form['title']
        value=request.form['value']
        variable=request.form['variable']
        task_table=Inputaken.query.filter_by(sno=sno).first()
        task_table.task_title=title
        task_table.task_value=value
        task_table.task_variable=variable
        db.session.add(task_table)
        db.session.commit()
        return redirect('/log')

    task_table=Inputaken.query.filter_by(sno=sno).first()
    return render_template('updatelog.html',taskupdate=task_table)  

@app.route("/log/delete/<int:sno>")
@login_required
def log_delete(sno):
    task_table=Inputaken.query.filter_by(sno=sno).first()
    db.session.delete(task_table)
    db.session.commit()
    return redirect("/log")    


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
