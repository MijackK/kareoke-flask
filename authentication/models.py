from app import db
from datetime import datetime
from sqlalchemy import func


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String)
    email = db.Column(db.String(60), unique=True)
    password = db.Column(db.String)
    admin = db.Column(db.Boolean, default=False)
    verify = db.Column(db.Boolean, default=False)

    def __init__(self, username, email, password):
        self.username = username
        self.email = email
        self.password = password


class PasswordReset(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(60))
    token = db.Column(db.String)
    date_created = db.Column(db.DateTime, default=datetime.now())
    date_updated = db.Column(db.DateTime, onupdate=func.now())
    used = db.Column(db.Boolean, default=False)

    def __init__(self, token, email):
        self.token = token
        self.email = email

    def is_valid(self):
        current_time = datetime.now()
        delta = current_time - self.date_created
        hours = delta.total_seconds() / 3600
        # change it so we get the hours limit from the config
        if hours < 24 and not self.used:
            return True
        return False


class EmailVerification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(60))
    token = db.Column(db.String)
    date_created = db.Column(db.DateTime, default=datetime.now())
    date_updated = db.Column(db.DateTime, onupdate=func.now())
    used = db.Column(db.Boolean, default=False)

    def __init__(self, token, email):
        self.token = token
        self.email = email

    def is_valid(self):
        current_time = datetime.now()
        delta = current_time - self.date_created
        hours = delta.total_seconds() / 3600
        # change it so we get the hours limit from the config
        if hours < 24 and not self.used:
            return True
        return False
