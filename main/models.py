from main import db,login_manager
from flask_login import UserMixin

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class Tracker(db.Model):
    sno=db.Column(db.Integer, primary_key=True)
    tracker_name=db.Column(db.String(300),nullable=False, unique=True)
    task_value_type=db.Column(db.String(20), nullable=False)

    def __repr__(self) -> str:
        return f"{self.sno} - {self.tracker_name} - {self.task_value_type}"
        
class User(db.Model,UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    image_file=db.Column(db.String(20), nullable=False, default='default.jpg')
    password = db.Column(db.String(60), nullable=False)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}')"