from turtle import update
from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app=Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI']="sqlite:///input.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=False
db=SQLAlchemy(app)


class inputaken(db.Model):
    sno=db.Column(db.Integer, primary_key=True)
    task_title=db.Column(db.String(300),nullable=False)
    task_value=db.Column(db.Integer, nullable=False)
    task_date=db.Column(db.DateTime,default=datetime.utcnow)
    task_variable=db.Column(db.String(20),nullable=False)

    def __repr__(self) -> str:
        return f"{self.sno} - {self.task_title}"
    
 
@app.route('/', methods=['GET','POST'])
def hello_world():
    if request.method=='POST':
        title=request.form['title']
        value=request.form['value']
        variable=request.form['variable']
        task_table=inputaken(task_title=title,task_value=value,task_variable=variable)
        db.session.add(task_table)
        db.session.commit()
    outputpage=inputaken.query.all()
    return render_template('index.html',outputpage=outputpage)

@app.route("/update/<int:sno>",  methods=['GET', 'POST'])
def update(sno):
    if request.method=='POST':
        title=request.form['title']
        value=request.form['value']
        variable=request.form['variable']
        task_table=inputaken.query.filter_by(sno=sno).first()
        task_table.task_title=title
        task_table.task_value=value
        task_table.task_variable=variable
        db.session.add(task_table)
        db.session.commit()
        return redirect('/')

    task_table=inputaken.query.filter_by(sno=sno).first()
    return render_template('update.html',taskupdate=task_table)



@app.route("/delete/<int:sno>")
def delete(sno):
    task_table=inputaken.query.filter_by(sno=sno).first()
    db.session.delete(task_table)
    db.session.commit()
    return redirect("/")



if __name__ =="__main__":
    app.run(debug=False, port=8000)
