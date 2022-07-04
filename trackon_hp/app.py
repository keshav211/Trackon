from enum import unique
from turtle import update
from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import exc, true
from datetime import datetime


app=Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI']="sqlite:///dashboard_input.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=False
db=SQLAlchemy(app)


class tracker(db.Model):
    sno=db.Column(db.Integer, primary_key=True)
    tracker_name=db.Column(db.String(300),nullable=False, unique=True)
    task_value_type=db.Column(db.String(20), nullable=False)

    def __repr__(self) -> str:
        return f"{self.sno} - {self.tracker_name} - {self.task_value_type}"
    
 
@app.route('/', methods=['GET','POST'])
def hello_world():
    if request.method=='POST':
        title=request.form['track_variable']
        variable=request.form['track_type']
        task_table=tracker(tracker_name=title,task_value_type=variable)
        if task_table not in db.session:
            try:
                db.session.add(task_table)
                db.session.commit()
            except exc.IntegrityError:
                db.session.rollback()
        else:
            return redirect("/")    
    outputpage=tracker.query.all()
    return render_template('index.html',outpage=outputpage)

@app.route("/delete/<int:sno>")
def delete(sno):
    task_table=tracker.query.filter_by(sno=sno).first()
    db.session.delete(task_table)
    db.session.commit()
    return redirect("/")   



if __name__ =="__main__":
    app.run(debug=True, port=5000)
