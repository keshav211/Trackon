from sqlalchemy.sql import func
from main import db, login_manager
from flask_login import UserMixin


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class Inputaken(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    task_title = db.Column(db.String(300), nullable=False)
    task_value = db.Column(db.Integer, nullable=False)
    task_date = db.Column(
        db.DateTime(timezone=True),default=func.now(), nullable=False)
    task_variable = db.Column(db.String(20), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    tracker_id = db.Column(db.Integer, db.ForeignKey(
        'tracker.sno'), nullable=False)

    def __repr__(self) -> str:
        return f"(value:'{self.task_value}', timestamp:'{self.task_date}')"

    def __getitem__(self, key):
        return self.__dict__[key]


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False,
                           default='default.jpg')
    password = db.Column(db.String(60), nullable=False)
    trackers = db.relationship('Tracker', backref='user', lazy=True)
    logs = db.relationship('Inputaken', backref='user', lazy=True)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}')"


class Tracker(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    tracker_name = db.Column(db.String(300), nullable=False, unique=True)
    task_value_type = db.Column(db.String(20), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    logs = db.relationship('Inputaken', backref='tracker', lazy=True)

    def __repr__(self) -> str:
        return f"{self.sno} - {self.tracker_name} - {self.task_value_type}"
